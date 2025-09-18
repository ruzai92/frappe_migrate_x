## FrappeMigrateX

Frappe custom bench migrate for specfic app.

Option: to disabled sync fixture
add --skip-fixtures

# Single app migration
```
bench --site mysite migrate-x --app erpnext --skip-fixtures
```

# Multiple app selection
```
bench --site mysite migrate-x --multi-app --skip-fixtures
```

# All options combined
```
bench --site mysite migrate-x --multi-app --skip-fixtures --skip-failing
```

The --multi-app flag now provides the interactive multiple app selection functionality, making the
option name more descriptive and intuitive for users.

#### License

MIT
