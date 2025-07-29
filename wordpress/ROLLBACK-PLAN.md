# Marketing Automation Rollback Plan

This document outlines the procedures for rolling back the marketing automation system in case of critical issues during or after deployment.

## Rollback Triggers

### Automatic Rollback (During Deployment)
- Deployment script failure
- Health check failures
- Service startup failures
- Configuration errors

### Manual Rollback (After Deployment)
- Critical system failures
- Data corruption
- Performance degradation
- Security vulnerabilities
- Business-impacting bugs

## Pre-Rollback Checklist

1. **Verify Backup Availability**
   - Confirm recent backups exist
   - Verify backup integrity
   - Document current system state

2. **Notify Stakeholders**
   - IT team
   - Marketing team
   - Management
   - Affected users

3. **Prepare Rollback Environment**
   - Allocate necessary resources
   - Document current configuration
   - Prepare rollback scripts

## Rollback Procedures

### 1. Database Rollback

```bash
# Stop services
systemctl stop apache2 mysql

# Restore database
mysql -u [username] -p[password] [database] < backup/db_backup_$(date +%Y%m%d).sql

# Verify restoration
mysql -u [username] -p[password] -e "USE [database]; SHOW TABLES;"

# Restart services
systemctl start mysql apache2
```

### 2. File System Rollback

```bash
# Navigate to web root
cd /var/www/encompass-msp

# Restore files from backup
tar -xzvf /backups/encompass-msp_$(date +%Y%m%d).tar.gz -C /var/www/

# Set permissions
chown -R www-data:www-data /var/www/encompass-msp
find /var/www/encompass-msp -type d -exec chmod 755 {} \;
find /var/www/encompass-msp -type f -exec chmod 644 {} \;
```

### 3. Configuration Rollback

```bash
# Restore configuration files
cp /backups/config/wp-config.php /var/www/encompass-msp/
cp /backups/config/.htaccess /var/www/encompass-msp/
cp -r /backups/config/plugins/ /var/www/encompass-msp/wp-content/

# Restore cron jobs
crontab -u www-data /backups/config/crontab_backup
```

## Post-Rollback Verification

1. **System Checks**
   - Verify all services are running
   - Check application logs for errors
   - Test critical user journeys

2. **Data Integrity**
   - Verify database content
   - Check file permissions
   - Test file uploads/downloads

3. **Performance**
   - Monitor system resources
   - Check response times
   - Verify caching is working

## Communication Plan

### Internal Communication
- **IT Team**: Immediate notification via Slack/email
- **Marketing Team**: Status update with impact assessment
- **Management**: Executive summary of issue and resolution

### External Communication (if needed)
- **Customers**: Status page update
- **Partners**: Direct communication if affected
- **Public Statement**: If service disruption is widespread

## Rollback Timeline

| Time | Action | Owner | Status |
|------|--------|-------|--------|
| T-1h | Verify backups | DevOps | Pending |
| T-45m | Notify stakeholders | PM | Pending |
| T-30m | Begin rollback | DevOps | Pending |
| T-15m | Verify rollback | QA | Pending |
| T-0 | System verification | DevOps | Pending |
| T+15m | Post-rollback testing | QA | Pending |
| T+30m | Full verification | DevOps | Pending |
| T+1h | Final sign-off | PM | Pending |

## Rollback Decision Matrix

| Issue Type | Severity | Rollback Required | Notes |
|------------|----------|-------------------|-------|
| Data loss | Critical | Yes | Immediate rollback |
| Security breach | Critical | Yes | Immediate rollback |
| System outage | High | Yes | Within 30 minutes |
| Performance degradation | Medium | No | Monitor first |
| Minor UI issues | Low | No | Document for next release |

## Rollback Contacts

| Role | Name | Contact |
|------|------|---------|
| IT Lead | [Name] | 555-0101 |
| Marketing Lead | [Name] | 555-0102 |
| DevOps | [Name] | 555-0103 |
| Management | [Name] | 555-0104 |

## Post-Rollback Actions

1. **Root Cause Analysis**
   - Document the issue
   - Identify contributing factors
   - Develop prevention plan

2. **System Updates**
   - Apply necessary patches
   - Update documentation
   - Schedule retraining if needed

3. **Follow-up**
   - Schedule review meeting
   - Update runbooks
   - Document lessons learned

## Appendix

### Rollback Scripts

#### Full Site Rollback
```bash
#!/bin/bash
# Full site rollback script

# Variables
BACKUP_DIR="/backups/encompass-msp"
SITE_DIR="/var/www/encompass-msp"
DB_USER="wordpress"
DB_PASS="yourpassword"
DB_NAME="wordpress"

# Stop services
echo "Stopping services..."
systemctl stop apache2 mysql

# Restore database
echo "Restoring database..."
zcat $BACKUP_DIR/db_backup_$(date +%Y%m%d).sql.gz | mysql -u$DB_USER -p$DB_PASS $DB_NAME

# Restore files
echo "Restoring files..."
tar -xzvf $BACKUP_DIR/encompass-msp_$(date +%Y%m%d).tar.gz -C /var/www/

# Set permissions
echo "Setting permissions..."
chown -R www-data:www-data $SITE_DIR
find $SITE_DIR -type d -exec chmod 755 {} \;
find $SITE_DIR -type f -exec chmod 644 {} \;

# Restart services
echo "Starting services..."
systemctl start mysql apache2

echo "Rollback complete. Please verify the site."
```

### Verification Checklist
- [ ] Homepage loads
- [ ] Admin dashboard accessible
- [ ] Forms submit data
- [ ] Emails are sending
- [ ] Plugins are active
- [ ] Custom functionality works
- [ ] No JavaScript errors
- [ ] All links work
- [ ] Media files display
- [ ] Search functionality works

### Common Rollback Scenarios

#### Scenario 1: Failed Plugin Update
1. Deactivate the plugin
2. Restore previous version from backup
3. Clear cache
4. Test functionality

#### Scenario 2: Database Corruption
1. Put site in maintenance mode
2. Restore latest database backup
3. Verify data integrity
4. Take site out of maintenance mode

#### Scenario 3: Theme Issues
1. Switch to default theme
2. Restore theme from backup
3. Clear cache
4. Reactivate custom theme

---
*Last updated: July 2025*  
*Version: 1.0.0*
