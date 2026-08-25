"""
Dependencies: chromadb, sentence-transformers
"""
import os
import glob
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any

class SOPKnowledgeBase:
    """
    Manages the ChromaDB vector store for standard operating procedures (SOPs).
    """
    
    def __init__(self, persist_dir: str = "data/chroma_db"):
        """
        Initialize the ChromaDB client and embedding model.
        
        Args:
            persist_dir (str): Path to store the persistent database.
        """
        self.persist_dir = os.path.abspath(persist_dir)
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # Initialize persistent client
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        
        # Use the requested all-MiniLM-L6-v2 embedding model
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name="sops",
            embedding_function=self.embedding_fn
        )

    def ingest_sops(self, sop_dir: str = "data/sops/") -> None:
        """
        Reads all .md files in the specified directory, splits them into SOP chunks,
        and ingests them into ChromaDB.
        
        Args:
            sop_dir (str): The directory containing markdown SOP files.
        """
        if not os.path.exists(sop_dir):
            print(f"Directory {sop_dir} does not exist. Nothing to ingest.")
            return

        md_files = glob.glob(os.path.join(sop_dir, "*.md"))
        ingested_count = 0
        
        for file_path in md_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Split file content by markdown headers (## )
            chunks = content.split("## ")
            
            for chunk in chunks:
                chunk = chunk.strip()
                if not chunk:
                    continue
                
                # The first line of the chunk is usually the SOP ID and title
                # e.g., "SOP-FLD-001: Flood Evacuation - Residential Area"
                lines = chunk.split('\n')
                header = lines[0].strip()
                body = '\n'.join(lines[1:]).strip()
                
                if ":" in header:
                    sop_id, title = header.split(":", 1)
                    sop_id = sop_id.strip()
                    title = title.strip()
                else:
                    sop_id = header[:15].strip()
                    title = header
                    
                # Extract hazard type from the SOP ID (e.g., FLD -> flood)
                hazard_type = "unknown"
                if "FLD" in sop_id:
                    hazard_type = "flood"
                elif "FIR" in sop_id:
                    hazard_type = "fire"
                elif "EQK" in sop_id:
                    hazard_type = "earthquake"
                elif "MED" in sop_id:
                    hazard_type = "medical"
                
                # Combine header back for full content context
                full_content = f"## {header}\n{body}"
                
                # Add to ChromaDB
                # Upsert handles inserting new or updating existing documents by ID
                self.collection.upsert(
                    ids=[sop_id],
                    documents=[full_content],
                    metadatas=[{
                        "title": title,
                        "hazard_type": hazard_type
                    }]
                )
                ingested_count += 1
                
        print(f"Ingested {ingested_count} SOPs from {len(md_files)} files.")

    def query(self, hazard_type: str, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Query the vector database for relevant SOPs.
        
        Args:
            hazard_type (str): The hazard type to filter by (or 'unknown' for no filter).
            query_text (str): The semantic query text.
            top_k (int): Number of top results to return.
            
        Returns:
            List[Dict[str, Any]]: List of retrieved SOPs with metadata and distance.
        """
        where_clause = None
        if hazard_type and hazard_type.lower() != "unknown":
            where_clause = {"hazard_type": hazard_type.lower()}
            
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k,
            where=where_clause
        )
        
        formatted_results = []
        if results['ids'] and len(results['ids']) > 0:
            ids = results['ids'][0]
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0] if 'distances' in results and results['distances'] else [0.0] * len(ids)
            
            for i in range(len(ids)):
                formatted_results.append({
                    "id": ids[i],
                    "title": metadatas[i].get("title", ""),
                    "hazard_type": metadatas[i].get("hazard_type", "unknown"),
                    "content": documents[i],
                    "distance": distances[i]
                })
                
        return formatted_results

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Returns statistical information about the ingested SOPs.
        
        Returns:
            Dict[str, Any]: Total SOP count and breakdown by hazard.
        """
        count = self.collection.count()
        # Since Chroma doesn't have aggregate group by, we can just fetch all metadatas
        # For a small SOP database, this is fine.
        all_data = self.collection.get(include=["metadatas"])
        
        by_hazard = {}
        if all_data and all_data['metadatas']:
            for meta in all_data['metadatas']:
                ht = meta.get("hazard_type", "unknown")
                by_hazard[ht] = by_hazard.get(ht, 0) + 1
                
        return {
            "total_sops": count,
            "by_hazard": by_hazard
        }

if __name__ == "__main__":
    print("Testing SOP Knowledge Base...")
    # Change working directory logic if needed, assumes running from root
    kb = SOPKnowledgeBase()
    kb.ingest_sops()
    
    stats = kb.get_collection_stats()
    print(f"Stats: {stats}")
    
    print("\nQuerying for 'people trapped in building' (Fire filter):")
    results = kb.query("fire", "people trapped in building", top_k=2)
    for r in results:
        print(f"- {r['id']}: {r['title']} (Dist: {r['distance']:.3f})")
