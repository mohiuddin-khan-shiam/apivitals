# Good First Issues for New Contributors

These issues are beginner-friendly, clearly scoped, and designed to welcome new open-source contributors to **ApiVitals**.

---

### Issue 1: Add Public Art Institute of Chicago API
- **Labels**: `good first issue`, `new-api`, `help wanted`
- **Description**: Add the Art Institute of Chicago public API (`https://api.artic.edu/docs/`) to `apis/art-culture/artic.yaml`.
- **Requirements**:
  - Create `apis/art-culture/artic.yaml`.
  - Category: `Art & Culture`.
  - Endpoint: `https://api.artic.edu/api/v1/artworks/129884`.
  - Verify with `uv run apivitals validate` and `uv run apivitals probe artic`.

---

### Issue 2: Add REST Countries v3 API
- **Labels**: `good first issue`, `new-api`
- **Description**: Add the REST Countries v3.1 API (`https://restcountries.com`) to `apis/geocoding/rest-countries.yaml`.
- **Requirements**:
  - Endpoint: `https://restcountries.com/v3.1/name/france`.
  - Auth: `none`.
  - Verify CORS and HTTPS support.

---

### Issue 3: Add `apivitals doctor` Diagnostic Subcommand
- **Labels**: `good first issue`, `enhancement`, `cli`
- **Description**: Add an `apivitals doctor` command that verifies the user's environment: checks if network connectivity is active, validates write access to `data/` and `site/`, and reports installed Python and uv versions.
- **Files to Edit**: `apivitals/cli.py`, `tests/test_cli.py`.

---

### Issue 4: Add Filter for SSL Days Remaining on Web Dashboard
- **Labels**: `good first issue`, `enhancement`, `frontend`
- **Description**: In `site/app.js` and `site/index.html`, add a filter checkbox or badge showing APIs whose SSL certificate expires in less than 30 days.
- **Files to Edit**: `apivitals/site_generator.py`.

---

### Issue 5: Add JSON Schema Export Command (`apivitals schema`)
- **Labels**: `good first issue`, `enhancement`, `developer-tools`
- **Description**: Implement a subcommand `apivitals schema` that outputs the JSON Schema for `ApiDefinition` using Pydantic's `ApiDefinition.model_json_schema()`. This will allow IDEs (like VS Code) to provide autocomplete when editing YAML files in `apis/`.
- **Files to Edit**: `apivitals/cli.py`, `tests/test_cli.py`.

---

### Issue 6: Add NASA Mars Rover Photos API
- **Labels**: `good first issue`, `new-api`
- **Description**: Add the NASA Mars Rover Photos endpoint to `apis/science/mars-rover.yaml`.
- **Endpoint**: `https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol=1000&api_key=DEMO_KEY`.
