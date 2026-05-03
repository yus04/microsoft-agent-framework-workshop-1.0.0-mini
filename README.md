# Microsoft Agent Framework Workshop (Mini)

[Microsoft Agent Framework](https://github.com/microsoft/agent-framework) を使って AI エージェントの基礎からマルチエージェントワークフローまでをハンズオン形式で学ぶワークショップです。

---

## 概要

このワークショップでは、10 本の Jupyter Notebook チュートリアルを通じて、以下の内容を段階的に習得します：

- Python 関数や MCP を使ったカスタムツールの定義
- シングルエージェントの構築（ツールなし／MCP ツールあり／Agent Skills あり）
- Azure AI Search を活用した RAG パターンの実装
- Azure AI Foundry への Hosted Agent デプロイ
- Foundry Agent Service を使ったエージェント構築
- HandoffBuilder によるマルチエージェントシステム
- SequentialBuilder / ConcurrentBuilder によるワークフロー構築

> **注意**: このワークショップは `agent-framework==1.0.0` に最適化されています。異なるバージョンでは API の変更により動作しない場合があります。

---

## チュートリアル一覧

| # | ノートブック | 内容 |
|---|------------|------|
| 01 | `01_custom_tools.ipynb` | Python 関数をカスタムツールとして定義し、天気取得・通貨換算などの機能をエージェントに持たせる |
| 02 | `02_mcp_tools.ipynb` | MCPStreamableHTTPTool を使って MCP サーバーのツール群をエージェントに組み込む |
| 03 | `03_single_agent_no_tools.ipynb` | Agent クラスの最小構成でシングルエージェントを構築する |
| 04 | `04_single_agent_mcp.ipynb` | MCP ツールを持つシングルエージェントを構築し、リアルタイムデータにアクセスする |
| 05 | `05_single_agent_skills.ipynb` | SkillsProvider と SKILL.md を使った Progressive Disclosure パターンによる Agent Skills |
| 06 | `06_ai_search_agent.ipynb` | Azure AI Search を検索ツールとして統合した RAG エージェントを構築する |
| 07 | `07_hosted_agent_deploy.ipynb` | azure-ai-projects SDK を使って Azure AI Foundry に Hosted Agent をデプロイする |
| 08 | `08_foundry_agent_service.ipynb` | FoundryChatClient で Azure AI Foundry Agent Service を使うエージェントを構築する |
| 09 | `09_multi_agent.ipynb` | HandoffBuilder でコーディネーター＋専門エージェントのマルチエージェントシステムを構築する |
| 10 | `10_workflow.ipynb` | SequentialBuilder（順次）と ConcurrentBuilder（並列）でエージェントワークフローを構築する |

---

## 前提条件

- Python 3.11 以上
- Azure サブスクリプション（Azure OpenAI Service へのアクセス）
- Azure OpenAI にデプロイされたモデル（`gpt-4.1-mini` など）
- 06：Azure AI Search リソース（Free または Basic プラン）
- 07〜08：[Azure AI Foundry](https://ai.azure.com) プロジェクトおよびモデルデプロイ

---

## クイックスタート

### 1. リポジトリをクローン

```bash
git clone https://github.com/yus04/microsoft-agent-framework-workshop-1.0.0-mini.git
cd microsoft-agent-framework-workshop-1.0.0-mini
```

### 2. 依存関係をインストール

```bash
bash setup.sh
# または手動で
pip install -r requirements.txt
```

### 3. 環境変数を設定

`.env.example` をコピーして `.env` を作成し、各値を設定します。

```bash
cp .env.example .env
```

`.env` に最低限以下の値を設定してください（使用するチュートリアルに応じて追加設定が必要です）：

```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_key_here
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_API_VERSION=2025-04-01-preview
USE_KEY_AUTH=True
```

### 4. チュートリアルを開始

VS Code で `01_custom_tools.ipynb` を開いて実行してください。

---

## MCP サーバー（02, 04, 09 で使用）

`mcp/mock_server.py` は Xbox Game Shop + CRM モックデータを提供する MCP サーバーです。ノートブック 02、04、09 の実行前に起動してください。

```bash
python mcp/mock_server.py
```

起動後、`http://localhost:8000/mcp` でツールが利用可能になります（`.env` の `MCP_SERVER_URI` に設定済み）。

---

## プロジェクト構成

```
microsoft-agent-framework-workshop-1.0.0-mini/
├── 01_custom_tools.ipynb          # カスタムツール定義
├── 02_mcp_tools.ipynb             # MCP ツール
├── 03_single_agent_no_tools.ipynb # シングルエージェント（ツールなし）
├── 04_single_agent_mcp.ipynb      # シングルエージェント（MCP ツールあり）
├── 05_single_agent_skills.ipynb   # Agent Skills
├── 06_ai_search_agent.ipynb       # Azure AI Search + RAG
├── 07_hosted_agent_deploy.ipynb   # Hosted Agent デプロイ
├── 08_foundry_agent_service.ipynb # Foundry Agent Service
├── 09_multi_agent.ipynb           # マルチエージェント（HandoffBuilder）
├── 10_workflow.ipynb              # ワークフロー（Sequential / Concurrent）
├── mcp/
│   └── mock_server.py             # Xbox Game Shop + CRM モック MCP サーバー
├── skills/                        # Agent Skills 定義（05 で使用）
│   ├── code-reviewer/
│   │   └── SKILL.md
│   └── travel-planner/
│       └── SKILL.md
├── .env.example                   # 環境変数のサンプル
├── requirements.txt               # Python 依存関係
└── setup.sh                       # セットアップスクリプト
```

---

## 使用技術

- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) — エージェント構築フレームワーク
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/) — LLM バックエンド
- [Azure AI Foundry](https://ai.azure.com/) — AI プロジェクト管理・エージェントサービス
- [Azure AI Search](https://learn.microsoft.com/azure/search/) — ドキュメント検索・RAG
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) — ツール統合プロトコル
- [FastMCP](https://github.com/jlowin/fastmcp) — MCP サーバー実装ライブラリ

---

## 謝辞

このワークショップは [nohanaga (Nobusuke Hanagasaki)](https://github.com/nohanaga) 氏のリポジトリ [microsoft-agent-framework-workshop-1.0.0](https://github.com/nohanaga/microsoft-agent-framework-workshop-1.0.0) を参考にして作成しました。充実したチュートリアル群を公開してくださった同氏に深く感謝いたします。
