# Troubleshooting Guide

This guide helps diagnose and resolve common issues with the Ralph Wiggum Manager.

---

## Quick Diagnostics

### Check Manager Status

```bash
python scripts/manager.py --vault-path ./vault --status
```

**Expected Output**:
```json
{
  "state": "idle",
  "running": false,
  "metrics": {
    "cycles_completed": 154,
    "items_processed": 47,
    "error_count": 2
  }
}
```

### Validate Vault Structure

```bash
python scripts/manager.py --vault-path ./vault --validate
```

**Expected Output**:
```
Validating vault structure
Creating missing folder: Inbox
Creating missing folder: Needs_Action
Vault structure validated
```

### Run Single Cycle Test

```bash
python scripts/manager.py --vault-path ./vault --single-cycle --verbose
```

---

## Common Issues

### Issue 1: Manager Won't Start

**Symptoms**:
- Manager exits immediately
- "Vault path does not exist" error
- Permission denied errors

**Diagnosis**:

```bash
# Check if vault path exists
ls -la /path/to/vault

# Check permissions
ls -ld /path/to/vault

# Verify Python version
python --version  # Should be 3.8+
```

**Solutions**:

1. **Create vault directory**:
```bash
mkdir -p /path/to/vault
python scripts/manager.py --vault-path /path/to/vault --validate
```

2. **Fix permissions**:
```bash
chmod 755 /path/to/vault
chown $USER:$USER /path/to/vault
```

3. **Use absolute path**:
```bash
# Instead of relative path
python scripts/manager.py --vault-path ./vault

# Use absolute path
python scripts/manager.py --vault-path /home/user/vault
```

---

### Issue 2: Stuck in Loop

**Symptoms**:
- Same cycle repeating
- No progress through stages
- Items not moving between folders

**Diagnosis**:

```bash
# Check current state
python scripts/manager.py --vault-path ./vault --status

# Check folder contents
ls -la vault/Inbox/
ls -la vault/Needs_Action/
ls -la vault/Pending_Approval/

# Check logs
tail -f logs/manager.log
```

**Solutions**:

1. **Reset state**:
```bash
# Stop manager
pkill -f manager.py

# Clear any lock files
rm -f vault/.manager.lock

# Restart
python scripts/manager.py --vault-path ./vault --continuous
```

2. **Manually move stuck items**:
```bash
# Move items to next stage
mv vault/Inbox/*.md vault/Needs_Action/
```

3. **Skip problematic stage**:
```python
# In manager.py, temporarily disable stage
def _process_inbox(self):
    self.logger.info("Skipping inbox processing")
    return True
```

---

### Issue 3: High Error Rate

**Symptoms**:
- Many failed operations
- Error count increasing
- Skills failing repeatedly

**Diagnosis**:

```bash
# View error log
grep ERROR logs/manager.log | tail -20

# Check skill status
python scripts/manager.py --vault-path ./vault --status | jq '.skills'

# Monitor in real-time
tail -f logs/manager.log | grep -E "ERROR|WARN"
```

**Solutions**:

1. **Identify failing skill**:
```bash
# Find most common errors
grep ERROR logs/manager.log | cut -d' ' -f5- | sort | uniq -c | sort -rn
```

2. **Disable problematic skill**:
```yaml
# In manager_config.yaml
skills:
  problematic_skill:
    enabled: false
```

3. **Increase retry limits**:
```yaml
error_handling:
  max_retries: 5
  retry_delay: 120
```

4. **Run in safe mode**:
```bash
# Skip failing skills
python scripts/manager.py --vault-path ./vault --safe-mode
```

---

### Issue 4: Skills Not Executing

**Symptoms**:
- Folders have items but skills don't run
- "Skill not available" warnings
- Skills show as disabled

**Diagnosis**:

```bash
# Check skill configuration
cat manager_config.yaml | grep -A5 "skills:"

# Verify skill scripts exist
ls -la ../*/scripts/*.py

# Check skill status
python scripts/manager.py --vault-path ./vault --status
```

**Solutions**:

1. **Enable skills in config**:
```yaml
skills:
  triage_inbox:
    enabled: true
  strategic_planner:
    enabled: true
```

2. **Verify trigger conditions**:
```python
# Check if triggers are met
def _check_trigger(self, trigger: str) -> bool:
    self.logger.debug(f"Checking trigger: {trigger}")
    # Add debug logging
```

3. **Test skill manually**:
```bash
# Run skill directly
cd ../triage-inbox
python scripts/triage.py --vault-path ../../vault
```

---

### Issue 5: Performance Issues

**Symptoms**:
- Slow cycle times
- High CPU/memory usage
- Timeouts

**Diagnosis**:

```bash
# Monitor resource usage
top -p $(pgrep -f manager.py)

# Check cycle times
grep "Cycle.*completed" logs/manager.log | tail -10

# Profile execution
python -m cProfile scripts/manager.py --vault-path ./vault --single-cycle
```

**Solutions**:

1. **Increase cycle interval**:
```bash
python scripts/manager.py --vault-path ./vault --continuous --interval 120
```

2. **Enable parallel processing**:
```yaml
parallel:
  enabled: true
  max_workers: 3
```

3. **Optimize folder scanning**:
```yaml
optimization:
  skip_empty_folders: true
  cache_enabled: true
  cache_ttl: 300
```

4. **Reduce logging verbosity**:
```yaml
logging:
  level: WARNING  # Instead of DEBUG
```

---

### Issue 6: Items Not Moving Between Folders

**Symptoms**:
- Items stuck in one folder
- No state transitions
- Manual moves required

**Diagnosis**:

```bash
# Check file permissions
ls -la vault/Inbox/*.md

# Verify frontmatter
head -20 vault/Inbox/item.md

# Check for file locks
lsof | grep vault
```

**Solutions**:

1. **Fix file permissions**:
```bash
chmod 644 vault/Inbox/*.md
```

2. **Verify frontmatter format**:
```markdown
---
type: task
priority: 1
status: new
---
```

3. **Manually trigger move**:
```python
# In skill script
import shutil
shutil.move('vault/Inbox/item.md', 'vault/Needs_Action/item.md')
```

---

### Issue 7: Configuration Not Loading

**Symptoms**:
- Default config used instead of custom
- Changes not taking effect
- "Config file not found" warnings

**Diagnosis**:

```bash
# Check config file exists
ls -la manager_config.yaml

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('manager_config.yaml'))"

# Check file path
python scripts/manager.py --vault-path ./vault --config manager_config.yaml --verbose
```

**Solutions**:

1. **Use absolute path**:
```bash
python scripts/manager.py --vault-path ./vault --config /full/path/to/manager_config.yaml
```

2. **Fix YAML syntax**:
```bash
# Validate and fix
yamllint manager_config.yaml
```

3. **Check file encoding**:
```bash
file manager_config.yaml  # Should be UTF-8
```

---

### Issue 8: Memory Leaks

**Symptoms**:
- Memory usage grows over time
- Eventually crashes
- Slow performance after long runs

**Diagnosis**:

```bash
# Monitor memory over time
while true; do
  ps aux | grep manager.py | grep -v grep
  sleep 60
done

# Use memory profiler
python -m memory_profiler scripts/manager.py --vault-path ./vault --single-cycle
```

**Solutions**:

1. **Restart periodically**:
```bash
# In cron
0 */6 * * * pkill -f manager.py && python scripts/manager.py --vault-path ./vault --continuous
```

2. **Clear caches**:
```python
# Add to cycle cleanup
def _cleanup_cycle(self):
    self.folders.clear()
    self._initialize_folders()
```

3. **Limit log file size**:
```yaml
logging:
  rotation: daily
  retention: 7
  max_size: 100MB
```

---

### Issue 9: Approval Queue Growing

**Symptoms**:
- Many items in Pending_Approval
- Approval bottleneck
- Workflow stalled

**Diagnosis**:

```bash
# Count pending approvals
ls vault/Pending_Approval/*.md | wc -l

# Check approval ages
ls -lt vault/Pending_Approval/

# Review approval policy
cat assets/approval_policies.yaml
```

**Solutions**:

1. **Process approvals**:
```bash
# Run approval monitor
cd ../approval-monitor
python scripts/approval_monitor.py --vault-path ../../vault
```

2. **Adjust approval policy**:
```yaml
# Auto-approve low-priority items
approval_policies:
  auto_approve:
    - priority: low
    - type: routine
```

3. **Batch approve**:
```bash
# Move all to approved
mv vault/Pending_Approval/*.md vault/Approved/
```

---

### Issue 10: Logs Growing Too Large

**Symptoms**:
- Disk space issues
- Slow log writes
- Large log files

**Diagnosis**:

```bash
# Check log sizes
du -sh logs/

# Find largest logs
ls -lhS logs/

# Check disk space
df -h
```

**Solutions**:

1. **Enable log rotation**:
```yaml
logging:
  rotation: daily
  retention: 30
  max_size: 10MB
```

2. **Compress old logs**:
```bash
gzip logs/*.log.1
```

3. **Clean old logs**:
```bash
find logs/ -name "*.log.*" -mtime +30 -delete
```

4. **Reduce log verbosity**:
```yaml
logging:
  level: WARNING
  sampling:
    enabled: true
    rate: 0.1
```

---

## Advanced Diagnostics

### Enable Debug Logging

```bash
python scripts/manager.py --vault-path ./vault --continuous --verbose
```

### Trace Execution

```python
# Add to manager.py
import sys
import trace

tracer = trace.Trace(count=False, trace=True)
tracer.run('main()')
```

### Monitor System Calls

```bash
strace -f -e trace=file python scripts/manager.py --vault-path ./vault --single-cycle
```

### Profile Performance

```bash
python -m cProfile -o profile.stats scripts/manager.py --vault-path ./vault --single-cycle

# Analyze results
python -m pstats profile.stats
```

---

## Error Messages Reference

### "Vault path does not exist"

**Cause**: Specified vault directory not found

**Fix**: Create directory or use correct path

### "Skill not available or disabled"

**Cause**: Skill not configured or disabled in config

**Fix**: Enable skill in manager_config.yaml

### "Circuit breaker opened"

**Cause**: Too many failures, circuit breaker triggered

**Fix**: Wait for timeout or fix underlying issue

### "Retry budget exhausted"

**Cause**: Too many retries in time window

**Fix**: Increase budget or reduce error rate

### "Permission denied"

**Cause**: Insufficient file/directory permissions

**Fix**: Adjust permissions with chmod/chown

---

## Getting Help

### Collect Diagnostic Information

```bash
# Create diagnostic bundle
tar -czf diagnostic.tar.gz \
  logs/ \
  manager_config.yaml \
  vault/*/

# Include system info
uname -a > system_info.txt
python --version >> system_info.txt
pip list >> system_info.txt
```

### Enable Verbose Logging

```bash
python scripts/manager.py --vault-path ./vault --continuous --verbose 2>&1 | tee debug.log
```

### Check Dependencies

```bash
pip check
pip list --outdated
```

---

## Prevention Best Practices

1. **Monitor regularly**: Check dashboard and logs daily
2. **Set up alerts**: Get notified of issues early
3. **Test changes**: Use dry-run mode before production
4. **Backup vault**: Regular backups prevent data loss
5. **Update dependencies**: Keep libraries current
6. **Review metrics**: Track trends over time
7. **Document issues**: Keep troubleshooting notes
8. **Test recovery**: Practice failure scenarios
9. **Capacity planning**: Monitor resource usage
10. **Health checks**: Regular validation runs
