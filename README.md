# sam-s3

AWS SAM を使うの 2 年ぶりぐらいなので、練習。 S3 バケットを 1 つ作る

このテンプレートは S3 単体でオブジェクトを HTTPS 公開する構成です。
S3 Website Endpoint は HTTPS 非対応のため、公開先は S3 REST API エンドポイントです。

## 公開ポリシー

- オブジェクトの `s3:GetObject` のみ外部公開
- `aws:SecureTransport=false` のアクセスは拒否
- ACL は使わず、Bucket Policy で公開制御
- SSE-S3 で保存時暗号化を有効化

## 最初のデプロイ

```sh
export AWS_PROFILE=xxxx
sam deploy -g
```

## 修正後のデプロイ

```sh
sam validate
cfn-lint template.yaml
#
export AWS_PROFILE=xxxx
sam build
sam deploy
```

## Cleanup

```bash
export AWS_PROFILE=xxxx
sam delete
```

## デプロイ後の確認

```sh
aws cloudformation describe-stacks \
	--stack-name sam-s3 \
	--query 'Stacks[0].Outputs'
```

`TestS3BucketHttpsEndpoint` が公開先です。
実際の閲覧は、その配下のオブジェクト URL で行います。
