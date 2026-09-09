# Full adapter development board

The only current design effort is [full-adapter](full-adapter/README.md).
It is in component qualification, **not a manufacturing release**. No new PCB
or fabrication files have been released.

The superseded root and compact boards were preserved in local checkpoint
`4353916` before removal. Recover a historical project into a separate checkout:

```sh
git worktree add --detach ../sierra-carrier-checkpoint 4353916
```

[Historical evidence](docs/legacy/README.md) and the reusable libraries remain.
Historical ERC/DRC reports do not validate the replacement design. No parts have
been ordered and no commits have been pushed.
