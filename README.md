# Let's Encrypt on TrueNAS

## Deploy Steps

- deploy environment
- issue first certificate
- run hook script
- run add-to-cron script

### Hook Steps

1. Ping TrueNAS Server
2. Import Certificate to TrueNAS
3. Find Imported Certificate ID
4. Apply new certificate id to System UI
5. Restart System UI
6. Apply new certificate id to S3, FTP, WebDAV, etc

## Thanks

<https://github.com/danb35/deploy-freenas>

<https://github.com/NiceLabs/omv-letsencrypt>
