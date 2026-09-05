# Minecraft BDS Discord Notifier

Minecraft公式のBDS配布情報を定期確認し、新しいLinux版Bedrock Dedicated Serverが公開されたらDiscord Webhookへ通知します。

現在の基準バージョンは `1.26.45.1` です。

## 仕組み

GitHub Actionsが毎時17分に実行され、Minecraft公式の配布情報API

`https://net-secondary.web.minecraft-services.net/api/v1.0/download/links`

から `serverBedrockLinux` の公式ダウンロードURLを取得します。

このAPIが返すURLは `https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-<version>.zip` です。

新しいバージョンならDiscord Webhookへ通知し、`state.json` を更新します。

## セットアップ

### 1. GitHubリポジトリを作る

このフォルダの内容をGitHubリポジトリにそのまま配置します。

公開リポジトリを推奨します。GitHubの公式ドキュメントでは、公開リポジトリで標準GitHub-hosted runnerを使うActionsは無料とされています。

### 2. Discord Webhookを作る

Discordの通知したいチャンネルでWebhookを作成し、Webhook URLをコピーします。

### 3. GitHub Secretを登録

Repository → Settings → Secrets and variables → Actions → New repository secret

Name:

`DISCORD_WEBHOOK_URL`

Value:

Discord Webhook URL

Webhook URLはGitHubのコードに直接書かないでください。

### 4. 初回確認

GitHubの Actions → Check Minecraft BDS → Run workflow で手動実行できます。

初回状態は `1.26.45.1` なので、公式側が `1.26.45.1` の場合は通知されません。

### 5. 通常運用

以後は毎時17分に自動チェックします。

例えば公式が `1.26.46.1` を公開すると、Discordに

`1.26.45.1 → 1.26.46.1`

として通知され、`state.json` も `1.26.46.1` に更新されます。

## 注意

- これは通知専用です。BDSの自動更新はしません。
- Minecraft公式の配布情報が変更された場合は修正が必要になる可能性があります。
- GitHub Actionsのscheduled workflowは厳密に毎時17分に実行される保証はなく、混雑時に遅れることがあります。
