# sam-s3

AWS SAM を使うの 2 年ぶりぐらいなので、練習。 S3 バケットを 1 つ作る

このテンプレートは S3 単体でオブジェクトを HTTPS 公開する構成です。
S3 Website Endpoint は HTTPS 非対応のため、公開先は S3 REST API エンドポイントです。

uv と poeThePoet があるとうれしい。

AWS SAM CLI は今回
[aws-sam-cli · PyPI](https://pypi.org/project/aws-sam-cli/)
にしてみました。 `uv sync` でどうぞ

## 公開ポリシー

- オブジェクトの `s3:GetObject` のみ外部公開
- `aws:SecureTransport=false` のアクセスは拒否
- ACL は使わず、Bucket Policy で公開制御
- SSE-S3 で保存時暗号化を有効化

## 最初のデプロイ

```sh
copy .env.template .env
# .env を修正
source .env
sam deploy -g
```

## 修正後のデプロイ

```sh
sam validate
sam validate --lint　# `cfn-lint template.yaml` と同じ
#
export AWS_PROFILE=xxxx
sam build
sam deploy
```

## ブラウザで開く

作った S3 バケットは https:でアクセスできるようにしてあるので
コンテンツをアップロードする

```sh
poe main upload
## 最後に URLが表示されるのでそれをブラウザで開く
```

## Cleanup

```bash
poe main delete
sam delete
```

## メモ: ZScaler the MITM が居る場合

Python はシステムの証明書ストアを見ないが、
boto3 は [AWS_CA_BUNDLE](https://docs.aws.amazon.com/boto3/latest/guide/configuration.html#using-environment-variables) に対応しているので
ZscalerRootCertificate.crt が証明書ストアに追加されていれば

```sh
# Debian/Ubuntu
export AWS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
# RHEL/CentOS
export AWS_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.crt
```

で行ける (MITM なので通信は秘匿されないのは当然)。
AWS SAM も boto3 を使っている。
