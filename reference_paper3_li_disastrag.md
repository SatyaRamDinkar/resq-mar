Generated for ResQ-MAR Capstone | DisastRAG: A Multi-Source Disaster Information Integration and Access System | Date: 2026-08-26

# Paper 3 Analysis: DisastRAG (Li et al., 2026)

## 1. BIBLIOGRAPHIC INFO
*   **Full APA Citation:** Li, B., Chen, Z., Yin, K., & Mostafavi, A. (2026). DisastRAG: A Multi-Source Disaster Information Integration and Access System Based on Retrieval-Augmented LLMs. *arXiv preprint*.
*   **Journal:** arXiv (Preprint) / alphaxiv
*   **Year:** 2026
*   **Authors & Affiliations:** Bo Li, Zhitong Chen, Kai Yin, and Ali Mostafavi.

## 2. PROBLEM ADDRESSED
*   **Information Integration Problem:** Effective disaster management requires rapid access to accurate information. However, during a crisis, vital information is scattered across completely different formats and silos. A dispatcher might need to cross-reference an official PDF manual, a live database of available resources, and a real-time news alert simultaneously.
*   **Sources of Data Mentioned:** Structured operational records (relational databases), unstructured institutional documents (SOPs, manuals), and dynamic external data (live web information, news, social media).
*   **Why Single-Source RAG is Insufficient:** Traditional RAG systems are "single-path"—they usually only embed and search through unstructured PDF text. They fail to query structured SQL databases or pull live data from the web, making them blind to the heterogeneous, time-sensitive nature of real disasters.

## 3. SYSTEM ARCHITECTURE
*   **Multi-Source Integration:** DisastRAG employs a **multi-path architecture**. Instead of a single vector database, the system routes the user's query to the most appropriate data silo based on the query's intent.
*   **Retrieval Mechanism:** 
    1.  **Document Retrieval Path:** Uses vector embeddings to search the curated hazard corpus (unstructured).
    2.  **Structured Access Path:** Uses LLMs to generate SQL/queries to retrieve data from relational disaster records.
    3.  **External Web Fallback:** Triggers a web search API for dynamic, real-time requests that fall outside the internal databases.
*   **Query Understanding and Strategy Routing:** A routing agent analyzes the incoming prompt and decides which of the three paths (or a combination) is required.
*   **Handling Conflicting Information:** The system utilizes a "Contextual Memory" module to maintain context and synthesize the final answer using the LLM, though the paper notes larger models are highly sensitive to noise from conflicting retrieval paths.

**ASCII Diagram:**
```text
               [ User Query ]
                     │
                     ▼
       +----------------------------+
       | Query Understanding &      |
       |      Strategy Router       |
       +----------------------------+
         │           │            │
  (Unstructured) (Structured)  (Live Web)
         │           │            │
         ▼           ▼            ▼
   +----------+ +----------+ +----------+
   | Document | | Relational|| External |
   | Retrieval| | Database | |   Web    |
   | (Vector) | | (Text2SQL)|| Fallback |
   +----------+ +----------+ +----------+
         │           │            │
         ▼           ▼            ▼
       +----------------------------+
       |   Contextual Memory &      |
       |   LLM Response Generation  |
       +----------------------------+
                     │
                     ▼
              [ Final Answer ]
```

## 4. DATA SOURCES & PROCESSING
*   **Data Sources Used:**
    1.  Curated hazard corpus (Unstructured Text)
    2.  Relational disaster records (Structured Data)
    3.  Web information (Dynamic/External)
*   **Preprocessing:** Unstructured texts are chunked, embedded via embedding models, and stored in a vector database. Structured data is maintained in a relational schema accessible via Text-to-SQL logic.
*   **Real-time vs. Batch:** The internal databases (vector and relational) act as the batch/static operational knowledge, while the web fallback path dynamically handles real-time queries for unfolding events.

## 5. EVALUATION
*   **Metrics:** Multiple-choice accuracy (for factual selections) and open-ended keypoint coverage (for complex information synthesis).
*   **Results:** Evaluated across four open-source LLMs. Retrieval augmentation consistently outperformed no-retrieval baselines.
*   **Comparison against Naive RAG:** The multi-source DisastRAG achieved multiple-choice accuracy gains of 12–23% and open-ended keypoint coverage improvements of up to +10.5% over single-source, naive RAG implementations. They also found that hybrid retrieval methods are best for open-ended coverage, while strict vector reranking is better for factual selections.

## 6. LIMITATIONS
*   **Missing Sources:** It does not natively integrate raw sensor streams (IoT, water level sensors) or raw visual data (drone feeds), relying mostly on text and database records.
*   **Offline Operation:** Web fallback fundamentally breaks during severe network outages. The paper does not heavily focus on edge-deployed SLMs for offline resilience.
*   **Scalability Concerns:** LLM-based query routing and Text-to-SQL generation introduce high latency, which can bottleneck a system under the heavy load of thousands of simultaneous citizen requests.
*   **Real-world Deployment Gaps:** Hallucinations in the Text-to-SQL path can lead to querying the wrong database tables, silently corrupting the structured access path during a crisis.

## 7. HOW THIS INFORMS RESQ-MAR
*   **Knowledge Base Inspiration:** ResQ-MAR will heavily draw from DisastRAG's "Strategy Routing" concept. We will upgrade our base ResQConnect RAG from a purely unstructured vector search into a **Multi-Source RAG**.
*   **Sources We Will Include:**
    1. Unstructured SOPs and Guidelines (ChromaDB)
    2. Structured real-time inventory and vehicle availability (Local SQLite/Pandas)
    3. Real-time Weather/Traffic APIs (when online)
*   **Multi-Source Integration:** In ResQ-MAR, our AutoGen `Orchestrator Agent` will be equipped with specialized tool-calling functions. Based on the user's prompt, it will dynamically choose whether to call the `search_vector_db` tool, the `query_inventory_db` tool, or both, synthesizing a response that perfectly fuses SOP guidelines with actual real-time resource availability.
