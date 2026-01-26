# UI Component Library (WIP)

**Status:** Work in progress - not yet production ready.

This is a shared React component library for the Intelli platform. It contains:

- **Async primitives** - Error boundaries, loading states, suspense wrappers
- **Agent components** - Autonomy slider, approval gates, reasoning panels, trust indicators
- **Canvas/spatial components** - Evidence canvas, provenance graph, semantic zoom
- **Pane components** - Document, governance, provenance, run explorer panes
- **UI primitives** - Buttons, badges, inputs, tabs, tooltips, etc.
- **Workbench** - Multi-pane workspace layout

## Known Issues

- Many unused imports (lint errors) - components are scaffolded but not fully implemented
- Not currently consumed by the main `ui/` app
- Needs proper build setup (package.json, tsconfig, etc.)

## Future Work

1. Fix lint errors (remove unused imports)
2. Add proper package.json with build scripts
3. Publish as internal package for use by `ui/` app
4. Add Storybook documentation

## For Devin

When working on frontend components:
- The **main app** is in `ui/src/`
- This library is **excluded from linting** until cleanup is done
- If you need shared components, check here first before creating new ones
