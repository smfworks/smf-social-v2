# SMF Social v2 - Docker Deployment

## Quick Start

```bash
# 1. Clone repository
cd /home/mikesai1/projects/smf-social-v2

# 2. Configure environment
cp .env.example .env
# Edit .env with your secure keys

# 3. Deploy
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# 4. Open browser
# http://localhost
```

## Configuration

### Required Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `JWT_SECRET` | JWT signing key | Required |
| `ENCRYPTION_KEY` | Token encryption key | Required |
| `PORT` | HTTP port | 80 |

### Optional Settings

```bash
# Debug mode (development only)
DEBUG=true

# Custom port
PORT=8080

# Custom domain
FRONTEND_URL=https://social.yourdomain.com
```

## Production Deployment

### 1. SSL/TLS (HTTPS)

Use Let's Encrypt with nginx-proxy:

```yaml
# Add to docker-compose.yml
services:
  nginx-proxy:
    image: nginxproxy/nginx-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/tmp/docker.sock:ro
      - ./certs:/etc/nginx/certs
    
  acme-companion:
    image: nginxproxy/acme-companion
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./certs:/etc/nginx/certs
```

### 2. Backup Strategy

```bash
# Backup data volume
docker run --rm -v smf-social-v2_smf-data:/data -v $(pwd):/backup alpine tar czf /backup/smf-backup-$(date +%Y%m%d).tar.gz -C /data .

# Restore
docker run --rm -v smf-social-v2_smf-data:/data -v $(pwd):/backup alpine tar xzf /backup/smf-backup-YYYYMMDD.tar.gz -C /data
```

### 3. Monitoring

Health endpoints:
- `GET /health` - Application health
- Docker health checks configured

### 4. Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d

# Verify
docker-compose ps
```

## Troubleshooting

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f nginx
```

### Reset Database

⚠️ **Warning: This deletes all data!**

```bash
docker-compose down
rm -rf data/*
docker-compose up -d
```

### Port Already in Use

```bash
# Change port in .env
PORT=8080

# Or stop existing service
sudo systemctl stop apache2
sudo systemctl stop nginx
```

## Architecture

```
┌─────────────┐
│    User     │
└──────┬──────┘
       │ HTTP/HTTPS
┌──────▼──────┐
│    Nginx    │ ← Reverse proxy, SSL termination
└──────┬──────┘
       │
   ┌───┴───┐
   │       │
┌──▼──┐ ┌──▼──┐
│React│ │API  │
│ UI  │ │     │
└─────┘ └──┬──┘
           │
     ┌─────▼─────┐
     │   SQLite  │ ← Persistent data
     └───────────┘
```

## Security Considerations

1. **Change default secrets** - Never use example values in production
2. **Firewall** - Only expose ports 80/443
3. **Updates** - Keep Docker images updated
4. **Backups** - Automated daily backups recommended
5. **HTTPS** - Always use SSL in production

## Support

- Documentation: See `/docs` directory
- Issues: GitHub Issues
- Logs: `docker-compose logs`
