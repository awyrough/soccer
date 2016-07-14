# soccer

### How to restore the database
- Go to the main directory of the django project `app/`

```
~/soccer:> cd app/
```

- If this is your first time, make the script executable

```
chmod 0775 scripts/restore.sh
```

- Run the script

```
./scripts/restore.sh
```

### How to import statistics event

```
> python manage.py populate_statistic_events --file <file>
```