# 頂流 AI + K8s + RAG 五大開源專案架構精要與個人技術棧實戰手冊
> **作者**: [@ecs7723158](https://github.com/ecs7723158)  
> **適用目標**: GitHub 綠點持續點亮、生產級雲原生 AI 架構沉澱、Notion 知識庫建構

---

## 🎯 目錄 (Table of Contents)
1. [GitHub 綠點（Contribution Graph）底層機制與刷綠防坑心法](#1-github-綠點底層機制與防坑心法)
2. [五大頂流專案深度剖析與「為我所用」精要](#2-五大頂流專案深度剖析)
   - [專案一：Kubernetes SIG Kueue (AI 批次與 GPU 配額調度)](#21-kueue-kubernetes-sigs-批次與-gpu-配額調度)
   - [專案二：KubeRay (Ray 分布式計算 K8s Operator)](#22-kuberay-ray-分布式計算-k8s-operator)
   - [專案三：KubeAI & vLLM (超高吞吐 LLM 推論與 Serving)](#23-kubeai--vllm-超高吞吐-llm-推論引擎)
   - [專案四：RAGFlow (深度文檔理解與多模態 RAG 引擎)](#24-ragflow-深度文檔理解與多模態-rag-引擎)
   - [專案五：Dify (全球 #1 開源 LLM 應用與 Multi-Agent 編排)](#25-dify-全球-1-開源-llm-應用與-multi-agent-編排)
3. [可直接複用的代碼模板與生產級實踐 (Actionable Recipes)](#3-可直接複用的生產級實踐)
4. [Notion 知識庫整合與自動化同步教學](#4-notion-知識庫整合教學)

---

## 1. GitHub 綠點底層機制與防坑心法

很多工程師常遇到一個困惑：「*明明天天寫代碼提交，為什麼 GitHub 主頁還是白白一片沒有綠點？*」

### 1.1 綠點點亮的四大官方必要條件
1. **Commit 郵箱必須與 GitHub 帳號綁定**：
   - 終端檢查：`git config user.email` 必須為 `ecs7723158@gmail.com`。
2. **分支必須是預設分支 (Default Branch)**：
   - 在你自己擁有的倉庫中，只有提交到 `main` 或 `master`（或指定的 default branch、gh-pages）才會記錄綠點。
   - 在非 default 分支（例如 `feature/xxx`）上的 commit，**直到該分支被合併回 default branch 前，都不會顯示綠點**。
3. **Fork 倉庫的嚴格限制（最常見陷阱）**：
   - **在 Fork 的倉庫提交代碼，預設「不會」計入貢獻圖表！**
   - 只有以下兩種情況會計入：
     - a. 提交的 Pull Request 被上游（Upstream）官方倉庫成功 **Merge**。
     - b. 將 Fork 倉庫分離獨立（Detached / Standalone Repo）或自己創建的原創倉庫。
4. **私有倉庫設定 (Private Contributions)**：
   - 如果你的倉庫是 Private，必須在 GitHub 個人主頁右上角點選「Contribution Settings」-> 勾選 **"Private contributions"**，否則私有 commit 只有自己能看到統計，公開頁面不顯示。

### 1.2 高質量可持續「綠點」養成作法
- **主倉庫日進一竿**：在個人的主力倉庫（例如 `k8s-ai-rag-stack`、`vibe-os`、`missav-vibe`）維持每天有功能迭代、測試增加、文檔精進或 CI 優化。
- **開源專案貢獻雙軌制**：
  - 在 Fork 倉庫建立規範分支（如 `feat/gpu-quota-dashboard`），提交高質量 PR 給官方。
  - 將研究成果、Helm Values 最佳實踐、架構演練代碼沉澱至自己的 `k8s-ai-rag-stack` 倉庫，保證 100% 綠點轉換！

---

## 2. 五大頂流專案深度剖析

---

### 2.1 Kueue (Kubernetes SIGs 批次與 GPU 配額調度)
- **官方倉庫**: `kubernetes-sigs/kueue` (Star ~3.6k)
- **技術棧**: Go, Kubebuilder, Kubernetes Controller-Runtime

#### 核心架構解析
在多團隊共用 K8s GPU 叢集的場景下，原生 K8s Default Scheduler 只做「單一 Pod」的資源滿足性過濾，缺乏「作業群體 (Gang Scheduling)」與「彈性配額」機制。Kueue 透過兩層抽象解耦：
1. **ClusterQueue**：全叢集層級的資源池，劃分 nominalQuota（名義配額）與 borrowingLimit（可借調上限）。
2. **LocalQueue**：Namespace 命名空間層級的排隊隊列，開發者只需將 Job 投遞至 LocalQueue。
3. **Cohort (資源共享聯盟)**：當團隊 A 的 GPU 閒置時，團隊 B 可自動借調；當團隊 A 突然提交高優先級 Job，Kueue 立即觸發 Preemption（搶占回收）。

#### 可為我所用的重點
- **Go Operator 控制器設計**：Kueue 是學習現代 Kubernetes Operator（使用泛型、Workload 狀態機、Reconcile 批次合併）的教科書範本。
- **生產告別 GPU 爭搶**：直接套用 `manifests/01-kueue/` 中的配置，可立即在任何 K8s 叢集實現 GPU 利用率從 30% 提升至 85% 以上。

---

### 2.2 KubeRay (Ray 分布式計算 K8s Operator)
- **官方倉庫**: `ray-project/kuberay` (Star ~4.5k)
- **技術棧**: Go, Ray Core, Python ML Ecosystem

#### 核心架構解析
Ray 是當前大模型分散式微調 (DeepSpeed/Megatron-LM) 與強化學習 (RLHF) 的事實標準。KubeRay 將 Ray 的核心動態轉化為 K8s CRD：
1. **RayCluster**：聲明 Head 節點與動態擴縮的 Worker 節點群。
2. **RayJob**：生命週期短暫的訓練作業，執行完畢後自動銷毀 Pod 釋放 GPU，避免遺忘佔卡。
3. **RayService**：針對 Ray Serve 的零停機滾動更新與流量分流。

#### 可為我所用的重點
- **動態節點搶佔與 Spot 實例整合**：KubeRay WorkerGroup 能夠設置為低成本的 Spot/Preemptible 實例，當節點被雲端商回收時，Ray 自動進行 Task-level 重算，省下 60% 算力費用。

---

### 2.3 KubeAI & vLLM (超高吞吐 LLM 推論引擎)
- **官方倉庫**: `vllm-project/vllm` (Star ~35k) & `kubeai-project/kubeai` (Star ~2.5k)
- **技術棧**: C++/CUDA, Python, PyTorch, Triton

#### 核心技術革命
1. **PagedAttention (分頁注意力機制)**：
   - 傳統推論框架必須為每個請求預先分配連續的固定最大長度顯存，造成 60%~80% 碎片化浪費。
   - vLLM 將 KV Cache 劃分為固定大小的 Block（如 16 個 Token），透過 Block Table 映射，將顯存浪費降至 4% 以下。
2. **連續批處理 (Continuous Batching)**：
   - 傳統架構是「等整批請求都生成完」才能處理下一批。
   - vLLM 在每次 Iteration（單個 Token 生成）粒度上動態加入新請求、剔除已完成請求，吞吐量提升 4 倍。
3. **Prefix Caching (前綴快取)**：
   - 對於 RAG 場景中重複出現的大型 System Prompt 或檢索到的共同文檔，vLLM 直接復用 KV Cache，大幅降低 TTFT。

#### 可為我所用的重點
- **KubeAI 的彈性冷啟動**：在 K8s 上利用 Concurrency 指標做 HPA，當沒有流量時縮容至 0，流量湧入時從本機快取目錄秒級拉起。

---

### 2.4 RAGFlow (深度文檔理解與多模態 RAG 引擎)
- **官方倉庫**: `infiniflow/ragflow` (Star ~28k)
- **技術棧**: Python, DeepDoc, Milvus/Elasticsearch, Vue3

#### 核心技術革命
傳統 RAG 框架（如早期的單純 LangChain 切分）只是簡單地按字數（如 500 字）切 chunk，直接破壞了 PDF/Word 中的表格關係與圖文排版，導致問答產生嚴重幻覺。
- **DeepDoc (視覺佈局解析)**：
  - 先透過視覺神經網絡識別頁面佈局（標題、正文、頁首、表格邊界）。
  - 對於跨頁複雜表格，精準解析出儲存格合併關係與行列關聯，還原結構化 Markdown。
- **Template-based Chunking**：針對論文、合約、財報、手冊採用截然不同的剖析器。

#### 可為我所用的重點
- **企業知識庫防幻覺金鑰**：在構建內部問答系統時，採用 RAGFlow 的 Parser 方案取代純文字切分，可使精確度直接翻倍。

---

### 2.5 Dify (全球 #1 開源 LLM 應用與 Multi-Agent 編排)
- **官方倉庫**: `langgenius/dify` (Star ~60k)
- **技術棧**: Python (Flask/Celery), Next.js, Redis, PostgreSQL

#### 核心架構解析
1. **DSL Workflow (領域特定語言工作流)**：
   - 將複雜的 Agent 思考鏈、條件判斷、循環重試、API 工具調用序列化為乾淨的 JSON/YAML DSL。
2. **Hybrid Search (混合檢索) + Reranker**：
   - 向量檢索 (語義相似度) + BM25 (關鍵字精確匹配) 雙路召回。
   - 透過 Cross-Encoder（如 `bge-reranker-large`）對 Top-50 候選段落重新計算注意力權重，過濾掉不相關噪聲。

#### 可為我所用的重點
- **生產級 Agent 狀態機設計**：Dify 的 Celery 異步隊列架構與串流 SSE (Server-Sent Events) 機制是設計高並發 AI Agent 平台的最佳參考對象。

---

## 3. 可直接複用的生產級實踐

本專案已在 `k8s-ai-rag-stack/` 中為您整合好所有模組配置：
- **Kueue GPU 調度實戰**：`manifests/01-kueue/cluster-queue.yaml`
- **KubeRay 分布式微調作業**：`manifests/02-kuberay/ray-job-finetune.yaml`
- **KubeAI / vLLM 高併發部署**：`manifests/03-kubeai-vllm/vllm-model-service.yaml`
- **RAGFlow 生產級 Helm 參數**：`manifests/04-ragflow/helm-values-prod.yaml`
- **Dify Agent API 與 Worker 編排**：`manifests/05-dify/dify-k8s-deployment.yaml`
- **推論首字延遲 (TTFT) 評測腳本**：`benchmarks/vllm_latency_benchmark.py`
- **RAG 混合檢索精準度評測**：`benchmarks/rag_retrieval_eval.py`

---

## 4. Notion 知識庫整合教學

本專案提供**兩種方式**將這份深度手冊同步到您的 Notion：

### 途徑一：使用自動化 Python 腳本直連同步
我們在 `scripts/sync_to_notion.py` 封裝了完整的 Notion API 模組：
```bash
# 設置您的 Notion 整合金鑰與目標頁面 ID
export NOTION_API_KEY="secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export NOTION_PAGE_ID="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 執行一鍵同步
python3 scripts/sync_to_notion.py
```

### 途徑二：免 API 一秒快速匯入
1. 打開個人 Notion 任意頁面。
2. 點擊右上角 `...` -> 選擇 `Import`。
3. 選擇 `Markdown & CSV`，上傳根目錄的 `NOTION_EXPORT.md`。
4. 即可在 Notion 中獲得排版精美、包含 Emoji Callout、Toggle 清單與語法高亮代碼塊的現代化知識庫！
