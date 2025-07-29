# Production Deployment Checklist

## Pre-Deployment

### Server Setup
- [ ] Provision production server(s) with required specs
- [ ] Configure operating system updates and security patches
- [ ] Set up firewall (UFW or similar)
- [ ] Configure SSH access with key-based authentication
- [ ] Set up time synchronization (NTP)
- [ ] Install required system packages (Python, PostgreSQL, Redis, Nginx)

### Database
- [ ] Install and configure PostgreSQL
- [ ] Create database and user
- [ ] Configure PostgreSQL for performance
- [ ] Set up regular backups

### Redis
- [ ] Install and configure Redis
- [ ] Configure Redis persistence
- [ ] Set up Redis authentication
- [ ] Configure Redis for production use

### Application Setup
- [ ] Clone the repository to `/opt/socialmedia`
- [ ] Create and activate virtual environment
- [ ] Install Python dependencies
- [ ] Create `.env` file with production settings
- [ ] Set proper file permissions

## Deployment

### Database Initialization
- [ ] Run database initialization script
```bash
python -m automation_stack.init_db
```
- [ ] Verify tables were created
- [ ] Load any initial data if needed

### Service Configuration
- [ ] Set up systemd service files
- [ ] Enable and start services
- [ ] Configure log rotation

### Web Server (Nginx)
- [ ] Install and configure Nginx
- [ ] Set up SSL certificates (Let's Encrypt)
- [ ] Configure reverse proxy
- [ ] Set up static file serving

## Post-Deployment

### Verification
- [ ] Test API endpoints
- [ ] Verify scheduled posts
- [ ] Check error logs
- [ ] Test notifications

### Monitoring
- [ ] Set up Prometheus and Grafana
- [ ] Configure alerting
- [ ] Set up log aggregation

### Backup
- [ ] Test backup and restore procedure
- [ ] Set up automated backups
- [ ] Verify backup integrity

## Security Hardening

### Application
- [ ] Disable debug mode
- [ ] Set secure cookie flags
- [ ] Configure CORS
- [ ] Set secure headers

### Server
- [ ] Disable root login
- [ ] Configure fail2ban
- [ ] Set up intrusion detection
- [ ] Regular security audits

## Maintenance

### Regular Checks
- [ ] Monitor disk space
- [ ] Check for updates
- [ ] Review logs
- [ ] Check backup status

### Updates
- [ ] Schedule maintenance windows
- [ ] Test updates in staging
- [ ] Backup before updates
- [ ] Document changes

## Rollback Plan

### If deployment fails
1. Stop the new services
2. Restore database from backup if needed
3. Revert to previous version
4. Restart old services
5. Investigate and document the issue

### Contact Information
- System Admin: [Name] - [Phone] - [Email]
- Developer: [Name] - [Phone] - [Email]
- Support: [Contact Info]

## Post-Deployment Documentation
- [ ] Update runbooks
- [ ] Document deployment process
- [ ] Update monitoring dashboards
- [ ] Schedule post-mortem if needed
