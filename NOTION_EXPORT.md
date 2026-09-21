# 🚀 雲原生 AI & RAG 頂流開源專案技術指南與 GitHub 綠點實戰手冊
> 👤 **作者與維護者**: [@ecs7723158](https://github.com/ecs7723158)  
> 🏷️ **技術領域**: Kubernetes, Generative AI, RAG, Distributed Computing, High-Throughput Inference  
> 📅 **更新時間**: 2026-09-21  

---

## 📌 模組一：GitHub 綠點（Contribution Graph）核心機制與避坑指南

> 💡 **核心洞察**：很多工程師天天寫程式，卻發現 GitHub 首頁依舊白白一片。這往往不是因為代碼沒寫好，而是觸碰了 GitHub 貢獻圖表的計算規則盲區！

### 🔍 綠點出現的 4 大官方硬性條件
- **郵箱必須精確綁定**：提交 Git Commit 時所用的 `user.email`（如 `ecs7723158@gmail.com`）必須已在 GitHub 帳號的 Emails 設定中完成驗證。
- **必須在預設分支 (Default Branch)**：在自己的倉庫中，只有提交到 `main` 或 `master`（或預設的 default branch）才會計入綠點。在 `feature` 分支上的 commit，只有在該分支被合併回 default branch 後才會被追溯計入。
- **Fork 倉庫限制（最大誤區）**：
  - **在 Fork 的倉庫內提交代碼，預設「完全不會」顯示綠點！**
  - 只有該分支的 Pull Request 被上游（Upstream）倉庫管理者正式 **Merge** 之後，綠點才會被點亮。
  - **最優解**：將專案架構演練與研究成果沉澱於個人原創的獨立倉庫（如 `k8s-ai-rag-stack`），每一筆 commit 保證 100% 點亮綠點！
- **私有倉庫展示開關**：若在 Private Repo 提交，需至 GitHub 個人頁面勾選「Contribution Settings」中的 **"Private contributions"**。

---

## 📌 模組二：五大頂流開源專案架構精髓與「為我所用」筆記

### 1️⃣ Kubernetes SIG Kueue (`kubernetes-sigs/kueue` - 3.6k ⭐)
- **領域**：K8s 批次與多租戶 GPU 配額排隊調度器
- **為我所用的亮點**：
  - **Cohort 資源動態借調**：解決 AI 團隊閒置時資源浪費、高峰時算力排隊的難題。
  - **Preemption 優先級搶占**：確保生產級在線訓練作業能夠隨時回收被低優先級作業借調的 GPU。
- **配置速查**：
```yaml
apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
  name: "cluster-queue-ai-team"
spec:
  cohort: "shared-ai-cohort"
  queueingStrategy: BestEffortFIFO
  preemption:
    reclaimWithinCohort: Any
    borrowWithinCohort:
      policy: LowerPriority
```

---

### 2️⃣ KubeRay (`ray-project/kuberay` - 4.5k ⭐)
- **領域**：Ray 分布式計算與大模型微調的 K8s Operator
- **為我所用的亮點**：
  - **RayJob 生命週期自管理**：訓練完畢自動回收 Pod，避免高價 GPU 被鎖死。
  - **Spot 搶佔式節點混部**：Worker 節點使用雲端商競價實例，利用 Ray 的容錯重算機制省下 60% 費用。

---

### 3️⃣ KubeAI & vLLM (`vllm-project/vllm` - 35k ⭐)
- **領域**：大模型超高吞吐推論 Serving 引擎
- **為我所用的亮點**：
  - **PagedAttention**：分頁式管理 KV-Cache，徹底解決注意力機制高達 80% 的顯存碎片浪費。
  - **Continuous Batching**：以 Iteration 為粒度動態拼裝批次，GPU 吞吐量提高 4 倍以上。
  - **Prefix Caching**：重複 System Prompt 秒級載入，大幅縮減首字反饋延遲 (TTFT)。

---

### 4️⃣ RAGFlow (`infiniflow/ragflow` - 28k ⭐)
- **領域**：深度文檔解析（DeepDoc）與多模態 RAG 引擎
- **為我所用的亮點**：
  - **拒絕純文字切塊**：傳統 LangChain 按字數切塊會破壞表格與上下文邏輯。
  - **視覺佈局感知**：採用視覺神經網絡精準識別財報、論文、合約中的合併儲存格與表格行列，大幅降低 RAG 幻覺。

---

### 5️⃣ Dify (`langgenius/dify` - 60k ⭐)
- **領域**：全球 #1 開源 LLM 應用與 Multi-Agent 視覺化編排
- **為我所用的亮點**：
  - **DSL 工作流引擎**：將 Agent 思考鏈與工具調用圖形化串接。
  - **混合檢索 (Hybrid Search) + Reranker**：結合 BM25 精準匹配與向量語義檢索，並透過 BGE-Reranker 交叉過濾噪音段落。

---

## 📌 模組三：個人技術資產庫一覽

本專案的所有生產級配置與自動化工具已同步發布於 GitHub：
- 🌐 **旗艦綜合專案**: [ecs7723158/k8s-ai-rag-stack](https://github.com/ecs7723158/k8s-ai-rag-stack)
- ⚙️ **微服務與串流優化**: [ecs7723158/missav-vibe](https://github.com/ecs7723158/missav-vibe)
- 🖥️ **混合操作系統框架**: [ecs7723158/vibe-os](https://github.com/ecs7723158/vibe-os)

### 5 大頂流專案個人優化分支一覽：
1. `ecs7723158/kueue` ➔ 分支 `feat/gpu-quota-dashboard`
2. `ecs7723158/kuberay` ➔ 分支 `feat/telemetry-prometheus-exporter`
3. `ecs7723158/kubeai` ➔ 分支 `perf/vllm-engine-benchmarks`
4. `ecs7723158/ragflow` ➔ 分支 `feat/k8s-helm-production-tuning`
5. `ecs7723158/dify` ➔ 分支 `feat/hybrid-search-reranker-zh`

---

## 📌 模組四：Notion 同步指南

### 快捷匯入法（無須 Token）
1. 打開個人 Notion 頁面。
2. 點選頁面右上角 `...` -> `Import`。
3. 選擇 `Markdown & CSV`，直接上傳本文件 `NOTION_EXPORT.md`。

### 命令列自動同步法
```bash
python3 scripts/sync_to_notion.py \
  --token "secret_your_notion_token" \
  --page-id "your_page_uuid" \
  --file "NOTION_EXPORT.md"
```
