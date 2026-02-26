# Deployment Guide

This guide covers deploying the Ralph Wiggum Manager in various environments.

---

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **OS**: Linux, macOS, or Windows
- **Memory**: 512MB minimum, 2GB recommended
- **Disk**: 1GB for logs and state
- **CPU**: 1 core minimum, 2+ cores for parallel processing

### Python Dependencies

```bash
pip install pyyaml watchdog
```

### Vault Structure

```
vault/
├── Inbox/
├── Needs_Action/
├── Pending_Approval/
├── Approved/
├── Rejected/
└── Done/
```

---

## Local Development

### Quick Start

```bash
# Clone or navigate to skills directory
cd .claude/skills/ralph_wiggum_manager

# Create vault structure
mkdir -p ../../vault/{Inbox,Needs_Action,Pending_Approval,Approved,Rejected,Done}

# Run single cycle test
python scripts/manager.py --vault-path ../../vault --single-cycle

# Run continuous mode
python scripts/manager.py --vault-path ../../vault --continuous --interval 60
```

### Configuration

Create `manager_config.yaml`:

```yaml
loop:
  enabled: true
  interval: 60
  max_cycles: 0

vault:
  path: "../../vault"
  folders:
    - Inbox
    - Needs_Action
    - Pending_Approval
    - Approved
    - Rejected
    - Done

skills:
  triage_inbox:
    enabled: true
    trigger: "inbox_not_empty"
    timeout: 300

  strategic_planner:
    enabled: true
    trigger: "needs_action_not_empty"
    timeout: 600

  approval_monitor:
    enabled: true
    trigger: "pending_approval_not_empty"

  executor:
    enabled: true
    trigger: "approved_not_empty"
    timeout: 900

  metric_auditor:
    enabled: true
    trigger: "done_updated"

logging:
  level: INFO
  file: logs/manager.log
```

### Testing

```bash
# Validate vault structure
python scripts/manager.py --vault-path ../../vault --validate

# Check status
python scripts/manager.py --vault-path ../../vault --status

# Run with verbose logging
python scripts/manager.py --vault-path ../../vault --single-cycle --verbose

# Dry run mode
python scripts/manager.py --vault-path ../../vault --dry-run
```

---

## Production Deployment

### Option 1: Systemd Service (Linux)

**Create service file**: `/etc/systemd/system/ralph-wiggum.service`

```ini
[Unit]
Description=Ralph Wiggum Manager - Autonomous Loop Orchestrator
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=app
Group=app
WorkingDirectory=/opt/vault
Environment="PYTHONUNBUFFERED=1"
ExecStart=/usr/bin/python3 /opt/vault/.claude/skills/ralph_wiggum_manager/scripts/manager.py --vault-path /opt/vault --continuous --interval 60
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Resource limits
MemoryLimit=2G
CPUQuota=80%

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/vault

[Install]
WantedBy=multi-user.target
```

**Enable and start**:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable ralph-wiggum

# Start service
sudo systemctl start ralph-wiggum

# Check status
sudo systemctl status ralph-wiggum

# View logs
sudo journalctl -u ralph-wiggum -f
```

**Manage service**:

```bash
# Stop
sudo systemctl stop ralph-wiggum

# Restart
sudo systemctl restart ralph-wiggum

# Disable
sudo systemctl disable ralph-wiggum
```

---

### Option 2: Docker Container

**Dockerfile**:

```dockerfile
FROM python:3.11-slim

# Install dependencies
RUN pip install --no-cache-dir pyyaml watchdog

# Create app directory
WORKDIR /app

# Copy skill files
COPY scripts/ /app/scripts/
COPY manager_config.yaml /app/

# Create vault mount point
RUN mkdir -p /vault

# Create logs directory
RUN mkdir -p /app/logs

# Run as non-root user
RUN useradd -m -u 1000 app && \
    chown -R app:app /app /vault
USER app

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
  CMD python /app/scripts/manager.py --vault-path /vault --status || exit 1

# Run manager
CMD ["python", "/app/scripts/manager.py", "--vault-path", "/vault", "--continuous", "--interval", "60"]
```

**Build and run**:

```bash
# Build image
docker build -t ralph-wiggum-manager:latest .

# Run container
docker run -d \
  --name ralph-wiggum \
  --restart unless-stopped \
  -v /path/to/vault:/vault \
  -v /path/to/logs:/app/logs \
  ralph-wiggum-manager:latest

# View logs
docker logs -f ralph-wiggum

# Check status
docker exec ralph-wiggum python /app/scripts/manager.py --vault-path /vault --status

# Stop container
docker stop ralph-wiggum

# Remove container
docker rm ralph-wiggum
```

**Docker Compose**:

```yaml
version: '3.8'

services:
  ralph-wiggum:
    build: .
    container_name: ralph-wiggum-manager
    restart: unless-stopped
    volumes:
      - /path/to/vault:/vault
      - ./logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "python", "/app/scripts/manager.py", "--vault-path", "/vault", "--status"]
      interval: 60s
      timeout: 10s
      retries: 3
      start_period: 30s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**Run with Docker Compose**:

```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

### Option 3: Kubernetes Deployment

**deployment.yaml**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ralph-wiggum-manager
  labels:
    app: ralph-wiggum
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ralph-wiggum
  template:
    metadata:
      labels:
        app: ralph-wiggum
    spec:
      containers:
      - name: manager
        image: ralph-wiggum-manager:latest
        imagePullPolicy: Always
        env:
        - name: PYTHONUNBUFFERED
          value: "1"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        volumeMounts:
        - name: vault
          mountPath: /vault
        - name: logs
          mountPath: /app/logs
        livenessProbe:
          exec:
            command:
            - python
            - /app/scripts/manager.py
            - --vault-path
            - /vault
            - --status
          initialDelaySeconds: 30
          periodSeconds: 60
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          exec:
            command:
            - python
            - /app/scripts/manager.py
            - --vault-path
            - /vault
            - --status
          initialDelaySeconds: 10
          periodSeconds: 30
      volumes:
      - name: vault
        persistentVolumeClaim:
          claimName: vault-pvc
      - name: logs
        emptyDir: {}
```

**pvc.yaml**:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: vault-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

**Deploy**:

```bash
# Create PVC
kubectl apply -f pvc.yaml

# Deploy application
kubectl apply -f deployment.yaml

# Check status
kubectl get pods -l app=ralph-wiggum

# View logs
kubectl logs -f deployment/ralph-wiggum-manager

# Scale (if needed)
kubectl scale deployment ralph-wiggum-manager --replicas=1

# Delete
kubectl delete -f deployment.yaml
```

---

### Option 4: Cron Job

For scheduled execution instead of continuous:

**crontab entry**:

```bash
# Run every 5 minutes
*/5 * * * * cd /opt/vault && python3 .claude/skills/ralph_wiggum_manager/scripts/manager.py --vault-path . --single-cycle >> logs/cron.log 2>&1

# Run every hour
0 * * * * cd /opt/vault && python3 .claude/skills/ralph_wiggum_manager/scripts/manager.py --vault-path . --single-cycle

# Run weekdays at 9 AM
0 9 * * 1-5 cd /opt/vault && python3 .claude/skills/ralph_wiggum_manager/scripts/manager.py --vault-path . --single-cycle
```

**Install crontab**:

```bash
# Edit crontab
crontab -e

# List crontab
crontab -l

# View cron logs
tail -f /var/log/cron
```

---

### Option 5: Windows Service

**Using NSSM (Non-Sucking Service Manager)**:

```powershell
# Download NSSM
# https://nssm.cc/download

# Install service
nssm install RalphWiggum "C:\Python39\python.exe" "C:\vault\.claude\skills\ralph_wiggum_manager\scripts\manager.py --vault-path C:\vault --continuous"

# Configure service
nssm set RalphWiggum AppDirectory "C:\vault"
nssm set RalphWiggum DisplayName "Ralph Wiggum Manager"
nssm set RalphWiggum Description "Autonomous Loop Orchestrator"
nssm set RalphWiggum Start SERVICE_AUTO_START

# Start service
nssm start RalphWiggum

# Check status
nssm status RalphWiggum

# Stop service
nssm stop RalphWiggum

# Remove service
nssm remove RalphWiggum confirm
```

---

## Monitoring and Observability

### Logging

**Configure structured logging**:

```yaml
logging:
  level: INFO
  file: logs/manager.log
  rotation: daily
  retention: 30
  structured: true
  include_context: true
```

**Log aggregation with ELK Stack**:

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /opt/vault/logs/manager.log
  json.keys_under_root: true
  json.add_error_key: true

output.elasticsearch:
  hosts: ["localhost:9200"]
```

### Metrics

**Export metrics to Prometheus**:

```python
# Add to manager.py
from prometheus_client import Counter, Gauge, start_http_server

cycles_total = Counter('manager_cycles_total', 'Total cycles completed')
items_processed = Counter('manager_items_processed', 'Total items processed')
error_count = Counter('manager_errors_total', 'Total errors')
cycle_duration = Gauge('manager_cycle_duration_seconds', 'Last cycle duration')

# Start metrics server
start_http_server(8000)
```

**Prometheus config**:

```yaml
scrape_configs:
  - job_name: 'ralph-wiggum'
    static_configs:
      - targets: ['localhost:8000']
```

### Alerting

**Alertmanager rules**:

```yaml
groups:
- name: ralph_wiggum
  rules:
  - alert: HighErrorRate
    expr: rate(manager_errors_total[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"

  - alert: ManagerDown
    expr: up{job="ralph-wiggum"} == 0
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Manager is down"
```

---

## Security

### File Permissions

```bash
# Vault directory
chmod 755 /opt/vault
chown app:app /opt/vault

# Skill files
chmod 644 /opt/vault/.claude/skills/ralph_wiggum_manager/scripts/*.py
chmod 755 /opt/vault/.claude/skills/ralph_wiggum_manager/scripts/manager.py

# Config files
chmod 600 /opt/vault/.claude/skills/ralph_wiggum_manager/manager_config.yaml
```

### Network Security

```bash
# Firewall rules (if exposing metrics)
sudo ufw allow 8000/tcp comment "Prometheus metrics"

# Restrict to localhost
sudo ufw allow from 127.0.0.1 to any port 8000
```

### Secrets Management

```yaml
# Use environment variables for secrets
skills:
  executor:
    api_key: "${EXECUTOR_API_KEY}"

# Or use secret management tools
# - AWS Secrets Manager
# - HashiCorp Vault
# - Kubernetes Secrets
```

---

## Backup and Recovery

### Backup Strategy

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/vault"
DATE=$(date +%Y%m%d)

# Backup vault
tar -czf "$BACKUP_DIR/vault-$DATE.tar.gz" /opt/vault

# Backup logs
tar -czf "$BACKUP_DIR/logs-$DATE.tar.gz" /opt/vault/logs

# Keep last 30 days
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

### Recovery

```bash
# Stop manager
sudo systemctl stop ralph-wiggum

# Restore vault
tar -xzf /backups/vault/vault-20260219.tar.gz -C /

# Validate structure
python scripts/manager.py --vault-path /opt/vault --validate

# Start manager
sudo systemctl start ralph-wiggum
```

---

## Performance Tuning

### Optimize Configuration

```yaml
optimization:
  skip_empty_folders: true
  batch_size: 10
  parallel_stages: true
  cache_enabled: true
  cache_ttl: 300

resources:
  max_cpu_percent: 80
  max_memory_mb: 2048
  max_connections: 50
```

### Database Optimization

If using database for state:

```sql
-- Add indexes
CREATE INDEX idx_items_status ON items(status);
CREATE INDEX idx_items_created ON items(created_at);

-- Vacuum regularly
VACUUM ANALYZE;
```

---

## Scaling

### Horizontal Scaling

For high-volume deployments:

```yaml
# Use distributed locking
locking:
  enabled: true
  backend: redis
  redis_url: "redis://localhost:6379"

# Partition by folder
partitioning:
  enabled: true
  strategy: folder
  workers:
    - folders: [Inbox, Needs_Action]
    - folders: [Pending_Approval, Approved]
    - folders: [Done]
```

### Load Balancing

```nginx
# nginx.conf
upstream ralph_wiggum {
    least_conn;
    server manager1:8000;
    server manager2:8000;
    server manager3:8000;
}

server {
    listen 80;
    location /metrics {
        proxy_pass http://ralph_wiggum;
    }
}
```

---

## Maintenance

### Regular Tasks

```bash
# Weekly
- Review error logs
- Check disk space
- Validate vault structure
- Update dependencies

# Monthly
- Rotate logs
- Archive old items
- Review metrics
- Update documentation

# Quarterly
- Performance review
- Security audit
- Disaster recovery test
- Capacity planning
```

### Updates

```bash
# Update manager
cd /opt/vault/.claude/skills/ralph_wiggum_manager
git pull

# Update dependencies
pip install --upgrade -r requirements.txt

# Test changes
python scripts/manager.py --vault-path /opt/vault --single-cycle --verbose

# Restart service
sudo systemctl restart ralph-wiggum
```

---

## Troubleshooting Deployment

See [troubleshooting.md](troubleshooting.md) for detailed troubleshooting guide.

### Quick Checks

```bash
# Service status
sudo systemctl status ralph-wiggum

# Recent logs
sudo journalctl -u ralph-wiggum -n 50

# Resource usage
top -p $(pgrep -f manager.py)

# Network connections
netstat -tulpn | grep python
```

---

## Best Practices

1. **Start small**: Begin with single-cycle mode, then move to continuous
2. **Monitor closely**: Watch logs and metrics during initial deployment
3. **Test thoroughly**: Use dry-run and single-cycle modes first
4. **Backup regularly**: Automate vault backups
5. **Document changes**: Keep deployment notes
6. **Plan for failure**: Test recovery procedures
7. **Secure properly**: Follow security best practices
8. **Update regularly**: Keep dependencies current
9. **Scale gradually**: Add resources as needed
10. **Review metrics**: Track performance over time
