# Alembic README

Generic single-database configuration.

## Creating Migrations

### Generate a Migration (autogenerate)
```bash
alembic revision --autogenerate -m "Create initial schema"
```

### Create an Empty Migration
```bash
alembic revision -m "Description of migration"
```

## Applying Migrations

### Upgrade to Latest
```bash
alembic upgrade head
```

### Upgrade to Specific Revision
```bash
alembic upgrade abc123def456
```

### Downgrade One Revision
```bash
alembic downgrade -1
```

### Downgrade All
```bash
alembic downgrade base
```

## Viewing Migration History
```bash
alembic history
```

## Viewing Current Version
```bash
alembic current
```
