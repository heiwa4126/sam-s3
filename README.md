# sam-s3

AWS SAM を使うの2年ぶりぐらいなので、練習。 S3バケットを1つ作る

## 最初のデプロイ

```sh
export AWS_PROFILE=xxxx
sam deploy -g
```

## 修正後のデプロイ

```sh
export AWS_PROFILE=xxxx
sam deploy
```

## Cleanup

```bash
export AWS_PROFILE=xxxx
sam delete
```
