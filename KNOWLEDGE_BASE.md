# AI Code Reviewer — Knowledge Base Document

This document describes every screen, section, element, and action in the AI Code Reviewer application.

---

## SCREEN INVENTORY

1. **Upload Screen** — Initial file upload interface
2. **Home Screen** — Workspace overview and file breakdown
3. **Dashboard Screen** — Advanced filters, search, tests, export, help
4. **Validation Screen** — Docstring quality checks and fixes
5. **DocStrings Screen** — Style conversion and generation
6. **Metrics Screen** — Workspace-wide export and reporting
7. **File Tabs** — Individual file editor and function breakdown

---

## [SCREEN: upload-screen]

**NAME:** Upload Screen

**DESCRIPTION:** Initial landing page where you upload Python files or zip archives to begin analysis. This is the onboarding screen you see when first opening the app.

**ELEMENTS:**

- **Upload Title** `⚡ AI Code Reviewer` — Large gradient title at the top of the centered glass panel. Identifies the application.

- **Tagline** `Docstring quality cockpit for Python workspaces` — Subtitle describing the app's purpose. Shown directly below the title.

- **Feature Cards Carousel** — Horizontal scrolling row of 8 cards describing key features. Cards auto-scroll and pause on hover. Each card shows an emoji, title, and brief description. Cards include: Instant Analysis, AI Docstring Fixing, Style Conversion, Three-Layer Validation, Auto Test Generation, Smart Dashboard, Flexible Exports, IDE-Like Interface.

- **Upload Helper Box** — Small info box with text: "Upload .py files or .zip source folders, then click Analyze Workspace."

- **File Uploader** — Drop zone accepting `.py` and `.zip` files. Dragging files over the zone highlights it with a yellow dashed border. Multiple files can be selected at once.

- **Analyze Workspace Button** — Large primary button (yellow outline, dark background) that triggers file parsing. Visible only after files are selected. Disabled if no files are uploaded.

- **Warning Alert** (conditional) — Appears only if the Analyze button is clicked with no files. Message: "Please upload at least one file."

**ACTIONS:**

- **Select files** → File uploader opens a system file picker. Can choose single or multiple `.py` or `.zip` files.

- **Drag files onto uploader** → Files are queued in the uploader. Button becomes clickable.

- **Click Analyze Workspace** → Full-screen loading overlay appears saying "Analyzing Workspace..." with a spinner. Files are parsed, workspace directories created, and the app transitions to the Home screen.

- **Parsing complete** → App switches to the Home screen, showing uploaded files in the sidebar and workspace metrics visible.

**STATES:**

- **Idle:** No files selected. Feature cards are visible. Analyze button is disabled (grayed out).

- **Files Selected:** Uploader shows list of queued files. Analyze button is enabled and clickable.

- **Loading:** Full-screen spinner overlays the entire page. Cannot interact with any elements.

- **Parse Error:** If parsing fails, an error message appears. "No valid Python files found."

- **Success:** App transitions to Home screen automatically.

**TIPS:**

- You can upload a mix of individual `.py` files and `.zip` archives containing multiple Python files. The app will extract and analyze all `.py` files from zips.

- If a file has syntax errors or cannot be parsed, the app will show it as "Parse Error" in the Home view, but won't block the entire upload.

- Multiple files can be selected in one upload action, speeding up onboarding.

- Once you upload files and click Analyze, you cannot go back to this screen from within a session unless you delete all files from the workspace.

**KNOWN ISSUES:**

- None documented.

**TIPS:**

- Running tests for the first time can be slow (10-30 seconds) if functions are being processed by the AI for the first time.

- Most tests are cached after the initial generation, so subsequent runs are much faster (under 5 seconds).

- Use "Clear Cache" to force regeneration of tests if you believe the cached versions are outdated. This deletes cached test files and regenerates them from scratch on the next run.

- You can view the source code of generated tests by clicking a function row; this helps verify test quality before using them in your CI/CD pipeline.

- Test generation failures are usually due to AI rate limits or network issues, not code problems. Retry after a few minutes or check your API quota.

**KNOWN ISSUES:**

**FAQ:**

Q: Why does it say a test is "skipped"?
A: Skipped means the AI generator couldn't create a test for that function. Common reasons: the function is a simple helper with no meaningful test, the API hit a rate limit during generation, or the code structure makes testing impractical. Retry with "Clear Cache" if you believe this was an error.

Q: What cached test data does the app keep?
A: The app caches AI-generated test suites per file. When you clear the cache, previously generated tests are deleted and regenerated from scratch on the next run.

Q: Why is the first run of Tests so slow?
A: The AI needs to analyze each function and generate test code for the first time. This can take 10-30 seconds for 50-100 functions. Subsequent runs are cached and much faster.

Q: What happens when I click "Clear Cache"?
A: This deletes all cached AI-generated tests, forcing a fresh generation on the next run. Use this if you update code and want fresh tests, or if cached tests seem outdated.

Q: Can I see the code of the generated tests?
A: Yes. Click on any function row in the tests table to open the File Tab, where you can view the generated test code. This helps you verify quality before copying tests into your actual test suite.

Q: Why did test generation fail for my function?
A: Common causes: your API quota was exceeded (ChatGPT/Claude rate limits), internet connection dropped, or the function's code is too complex for the AI to test. Wait a few minutes and retry, or check your API account status.

Q: Do tests regenerate every time I open the Tests tab?
A: No. The app uses cached tests if they exist. Tests only regenerate when you click "Generate" or "Clear Cache" then generate again. This keeps the UI fast and reduces AI API usage.

Q: Can I generate tests for just one file instead of the whole workspace?
A: Not from the Tests tab. To focus on specific files, use the Sidebar to deselect unwanted files, then generate. This regenerates tests only for the selected files.

Q: Why should I look at tests before using them in my CI/CD?
A: Generated tests are automatically created, but AI sometimes makes assumptions. Always review the test code to ensure it matches your actual code logic and doesn't skip important edge cases.

Q: What causes zero tests to be shown?
A: Either you selected "Show 0" (show no tests), all functions were skipped, or tests haven't been generated yet. Click "Generate" to start the process, or clear filters in the view options.

Q: Why is the Analyze Workspace button grayed out?
A: The button is disabled until you select at least one .py or .zip file in the uploader. Select your files first, then the button will become enabled and clickable.

Q: How long does the "Analyzing Workspace" step take?
A: Usually 5–30 seconds depending on file count and size. Very large files or many files may take longer.

Q: Can I go back to this upload screen after I've uploaded files?
A: Not from within the same session. To reset, delete all files from the workspace via the sidebar, then the app will automatically redirect back to the upload screen.

Q: What file types are accepted in the uploader?
A: Only .py (Python source files) and .zip (compressed archives). Other file types like .txt, .json, or .pyc are not accepted.

Q: Does the app work offline?
A: The upload and parsing step works offline. However, AI-powered features (docstring fixing, conversion, generation, and test generation) require internet access and API keys configured for AI models.

Q: What happens to my files if I close the browser?
A: All files and workspace data are cleared immediately when you close the app. They are not stored on any server. If you want to keep your files, download them before closing the app.

[/SCREEN]

---

## [SCREEN: home-screen]

**NAME:** Home Screen

**DESCRIPTION:** Workspace overview showing summary metrics for all files, functions, and docstring coverage. This is the first main screen you see after uploading files.

**ELEMENTS:**

- **Screen Header** — Large icon (🏠) and title "Home" in a frosted glass container at the top.

- **Metric Cards Grid** — 9 cards arranged in 3 rows of 3, each showing a key metric with a large number. Cards are styled with a glass effect and have a colored left border matching the theme. Metrics are:

  Row 1:
  - Total Files: Shows the count of uploaded files.
  - Files Having Doc String: Shows how many files have at least one documented function. Color-coded: green if all, yellow if some, red if none.
  - Total No. of Functions: Shows total function count across all files.

  Row 2:
  - Functions Having Doc String: Count with green/yellow/red color based on percentage.
  - Functions Not Having Doc String: Count with color coding.
  - Coverage Percentage: Shows `X.X%` or `N/A`. Green at 100%, red at <50%, yellow in between. Gray if no functions exist.

  Row 3:
  - Clean Files / Total Files: Shows ratio like `5 / 7` with color coding.
  - 100% Compliant Functions: Shows count of functions with zero validation errors.
  - Total Docstring Violations (PEP/Params): Shows count of rule violations across all docstrings.

- **File Breakdown Section** — Titled "📁 File Breakdown". Contains collapsible expanders, one per uploaded file.

- **File Expander** (per file) — Each expander shows:
  - Icon indicating file status (🟢 for 100% coverage, 🟡 for partial, 🔴 for poor, ⚪ for no functions).
  - File name.
  - When expanded, shows:
    - Detected Style: The docstring style detected in the file (Google, reST, NumPy, Mixed, or None/Incomplete).
    - **[WARNING]** if file is "Mixed": Yellow alert saying "Mixed Styles Detected: This file contains multiple different docstring formats. We highly recommend using the Style Converter below to normalize them into a single style."
    - Total Functions, Functions with Docstrings, Functions missing Docstrings, Coverage percentage.
    - Function details list showing each function name, lines, and whether it has a docstring.

**ACTIONS:**

- **Click a File Expander** → File details expand to show all functions and metrics for that file.

- **Open Dashboard** (from Navigation) → Switches to Dashboard screen. Dashboard tab is automatically added to the tab bar.

- **Open Validation** → Switches to Validation screen. Shows PEP errors and gives options to fix.

- **Open DocStrings** → Switches to DocStrings screen. Used to convert or generate docstrings.

**STATES:**

- **Empty:** If no files are uploaded, shows "No files uploaded." message.

- **Files Loaded:** Metric cards populate with real data. File expanders appear.

- **No Functions:** If a file has no functions, the expander shows "No Functions found."

- **Parse Error:** If a file failed to parse, expander shows error message instead of metrics.

**TIPS:**

- Use Home as your starting point after uploading. It gives you a quick overview: how many files you have, how many functions, and what percentage are documented.

- Color-coded metrics make it easy to spot weak areas at a glance: green = good, yellow = partial, red = needs work.

- Check the "Mixed Styles Detected" warning if it appears. It means your file uses multiple docstring formats (e.g., some Google-style and some reST-style). The Style Converter can fix this.

- The "Total Docstring Violations" count on Home tells you how many PEP or parameter-documentation errors exist. Higher numbers = more work needed in Validation tab.

**KNOWN ISSUES:**

- None documented.

**FAQ:**

Q: What do the colored metric cards mean?
A: Green means excellent (100% or all documented), yellow means partial or warning (some issues), and red means poor or critical (mostly undocumented or many errors). Gray means the metric is not applicable.

Q: Why do some files show a "Mixed Styles Detected" warning?
A: Your file contains multiple different docstring formats (e.g., some Google-style and some reST-style mixed together). Use the DocStrings tab to convert all docstrings to a single consistent style.

Q: How is Coverage Percentage calculated?
A: It's the number of functions with docstrings divided by the total number of functions, multiplied by 100. A file with 8 documented functions out of 10 total functions would show 80% coverage.

Q: Can I expand multiple file expanders at the same time?
A: Yes. You can click to expand any number of file expanders, and they will all remain open simultaneously. Click again to collapse any individual file.

Q: What should I do if a file shows "Parse Error"?
A: The file likely has Python syntax errors that prevented the parser from reading it. Check the file for issues like mismatched brackets, indentation problems, or invalid syntax, then re-upload the corrected file.

Q: If a file has zero functions, what coverage does it show?
A: Files with no functions show "N/A" for coverage percentage, since there's nothing to document. This typically indicates the file contains only imports, constants, or class definitions without any function definitions.

Q: Why would Coverage Percentage show as N/A but I have files uploaded?
A: This means your workspace has zero functions across all files. Check your uploaded files to ensure they contain function definitions.

Q: Can I delete a file from the Home screen?
A: No, deletion is not available from Home. Go to the sidebar on the left, find the file, and click the trash icon to delete it.

Q: What's the difference between "Files Having Doc String" and "Functions Having Doc String"?
A: "Files Having Doc String" counts how many of your uploaded files contain at least one documented function. "Functions Having Doc String" counts the exact number of individual functions that are documented, which can be much larger if you have many functions per file.

Q: How often do the metric cards update?
A: Metrics update instantly whenever you make a change (upload new files, apply AI fixes, convert docstrings, or run validation). No manual refresh or button click required.

[/SCREEN]

---

## [SCREEN: dashboard-screen]

**NAME:** Dashboard Screen

**DESCRIPTION:** Central hub for advanced analysis, filtering, searching, testing, and exporting. Appears as the "📊 Dashboard" tab after you click "Dashboard" in navigation. Contains 5 sub-tabs accessed via a frosted glass nav bar.

**ELEMENTS:**

- **Screen Header** — Large icon (🎛️) and title "Dashboard" in a frosted glass container at the top.

- **Dashboard Tab Navigation Bar** — Frosted glass bar with 6 controls:
  - `🎛️ Dashboard` text label (leftmost).
  - `🔍 Advanced Filters` button — Opens the filters sub-tab.
  - `🔎 Search` button — Opens the search sub-tab.
  - `🧪 Tests` button — Opens the tests sub-tab.
  - `📥 Export` button — Opens the export sub-tab.
  - `💡 Help` button — Opens the help sub-tab.
  Active tab button is highlighted in purple with a glow effect. Other buttons are gray and activate on click.

- **Dashboard Sub-Tab Content** — Below the nav bar, content changes based on selected sub-tab. See sub-screen documentation below for details on each.

**ACTIONS:**

- **Click any Dashboard sub-tab button** → Content area updates to show that sub-tab's interface.

- **All sub-tabs** → See below for specific actions within each sub-tab.

**STATES:**

- **Default:** "Advanced Filters" tab is active on first visit.

- **Tab Active:** Clicked tab button shows purple highlight and glow.

- **No Data:** If no files are uploaded, info message shows "Upload Python files first to use the Dashboard."

**TIPS:**

- Dashboard is where most of your analysis work happens. Start here after Home to dig deeper into specific issues.

- Use the Dashboard tab bar at the top to switch between different types of work (filtering, searching, testing, exporting, or getting help).

- Each sub-tab is independent: filter results don't affect search, test results, or exports.

[/SCREEN]

---

## [SCREEN: dashboard-advanced-filters]

**NAME:** Dashboard / Advanced Filters Sub-Tab

**DESCRIPTION:** Filter all functions in your workspace by documentation status, file, validation status, and sort order. View results in a live table with instant metrics updates.

**ELEMENTS:**

- **Panel Header** — Icon (🔍) and title "Advanced Filters" with subtitle "Filter functions by documentation status and get a quick quality snapshot for your current workspace."

- **Metric Cards** — 4 cards showing live counts:
  - Total Functions: Total functions across all files.
  - Has Doc String: Count of functions with docstrings.
  - Showing: Count currently displayed after filters are applied.
  - Workspace Shown: Percentage of total functions showing after filters.

- **Filter Controls** — 4 dropdown selectors in a row:
  - **Doc string:** Dropdown with options "All", "Has doc string", "No doc string". Default: "All".
  - **File:** Dropdown with options "All files" plus list of uploaded files. Default: "All files".
  - **Check result:** Dropdown with options "Any", "Looks good", "Has issues", "Not checked". Default: "Any".
  - **Sort by:** Dropdown with 5 options:
    - "Function name (A-Z)" — Alphabetical ascending.
    - "Function name (Z-A)" — Alphabetical descending.
    - "File name (A-Z)" — By file, then by line number.
    - "Line number (Low-High)" — By line number within file.
    - "Most validation issues" — By error count, highest first.
    Default: "Function name (A-Z)".

- **Results Table** — Displays after filters are applied. Columns are:
  - Function: Function name (searchable).
  - File: File name.
  - Doc String: "Has doc string" or "No doc string".
  - Check Result: "Looks good", "Has issues", or "Not checked".
  - Issues: Count of validation errors.
  - Line: Starting line number of the function.

- **Download Button** — `⬇️ Download Filtered Results` — Downloads the current filtered table as CSV file.

**ACTIONS:**

- **Change any filter** → Table updates instantly to show only matching rows. Metric cards update to reflect new counts.

- **Click a column header** → Table rows can be sorted by that column (if Streamlit allows native sorting).

- **Click Download Filtered Results** → CSV file downloads with the currently visible rows.

**STATES:**

- **All Selected:** Shows all functions in workspace. Table may be large.

- **Filters Applied:** Table narrows to matching rows. "Showing" and "Workspace Shown %" metrics update.

- **No Matches:** If filters result in 0 functions, shows info message "No functions match the selected filter combination."

- **Download Ready:** CSV file is generated with current filter state.

**TIPS:**

- Use filters to focus on a specific problem: e.g., "No doc string" + "Any" validation status shows all undocumented functions.

- Use "Check result" = "Has issues" to find functions with validation errors that still have docstrings (indicating low-quality documentation).

- Sort by "Most validation issues" to prioritize which functions to fix first.

- Download the filtered results and share with your team to show which functions need attention.

**KNOWN ISSUES:**

- None documented.

**FAQ:**

Q: How do I apply multiple filters at once?
A: Each filter selector is independent. Select your values for Doc string, File, Check result, and Sort by in any order. The table updates instantly to reflect all active filters combined.

Q: What does "Workspace Shown" mean in the metrics?
A: It's the percentage of your total functions that are currently visible after applying filters. If you have 100 functions total and 50 are showing, "Workspace Shown" would be 50%.

Q: Can I reset all filters to show everything again?
A: Yes. Set Doc string to "All", File to "All files", and Check result to "Any". The table immediately shows all functions again.

Q: What's the difference between sorting by "Function name (A-Z)" and "Line number (Low-High)"?
A: "Function name (A-Z)" sorts alphabetically regardless of which file the function is in. "Line number (Low-High)" sorts by file first, then by the line where the function appears within that file.

Q: How do I find all functions with validation errors?
A: Set Check result to "Has issues" in the filters. The table then shows only functions that have broken validation rules.

Q: Can I export only the filtered results?
A: Yes. The "Download Filtered Results" button exports only the rows currently visible after your filters are applied, not the entire workspace.

Q: Why would I filter by "Check result" = "Not checked"?
A: Functions show "Not checked" if they have no docstring at all. Filtering for this helps you find functions that are completely undocumented and need docstrings generated.

Q: If I change a filter, do my previous filter settings get saved?
A: No. Filter settings are only maintained during your current session. If you refresh the page or close the app, filters reset to defaults.

Q: Can I sort by multiple columns?
A: No. The "Sort by" dropdown allows only one sort order at a time. Choose the primary sort that matters most to you.

Q: What if my filtered result shows zero functions?
A: This means no functions in your workspace match the selected filter combination. Try broadening your filters (e.g., "All" instead of a specific file) to see if any functions match.

[/SCREEN]

---

## [SCREEN: dashboard-search]

**NAME:** Dashboard / Search Sub-Tab

**DESCRIPTION:** Search for functions by name or file name across your entire workspace. Results appear in a live table with real-time metrics.

**ELEMENTS:**

- **Panel Header** — Icon (🔎) and title "Search Functions" with subtitle "Case-insensitive search across all parsed functions with consistent metrics and results table output."

- **Metric Cards** — 3 cards showing:
  - Total Functions: Total functions across all files.
  - Showing: Count of matched functions.
  - Workspace Shown: Percentage of total functions matched.

- **Search Input** — Text box with placeholder "Search by function or file name...". Accepts any text. Search is case-insensitive. Pressing Enter applies the search.

- **Search Helper Note** — Small text below search box: "Type your search text, then press Enter to apply it."

- **Results Table** — Displays after search is applied. Columns are:
  - Function: Function name.
  - File: File name.
  - Doc String: "Has doc string" or "No doc string".
  - Check Result: Validation status ("Looks good", "Has issues", "Not checked").
  - Line: Starting line number.

**ACTIONS:**

- **Type text in search box** → Table content doesn't update until Enter is pressed (reduces unnecessary re-renders).

- **Press Enter** → Search is applied. Table updates immediately.

- **Clear search box** → Shows all functions again (full workspace).

- **Each row in results** → Can be inspected; no drill-down available from Search (use Dashboard or file tabs for details).

**STATES:**

- **Empty search:** Shows all functions.

- **Search Applied:** Shows only functions matching the query in name or file path.

- **No matches:** Info message "No functions match the criteria."

**TIPS:**

- Use Search to quickly locate a specific function across multiple files. Example: search "calculate" to find all functions with "calculate" in the name.

- Search also matches file names: searching "utils" will show all functions in files with "utils" in the path.

- Search is case-insensitive, so "Calculate", "calculate", and "CALCULATE" all return the same results.

- Search results show the validation status, making it easy to find a function and see if it has issues without opening the full file.

**KNOWN ISSUES:**

- None documented.

**FAQ:**

Q: How do I clear my search and see all functions again?
A: Clear the text in the search box (leave it empty) and press Enter. The table immediately shows all functions again.

Q: Is search case-sensitive?
A: No. Search is case-insensitive, so searching "Calculate", "calculate", or "CALCULATE" returns the same results.

Q: Can I search for partial words?
A: Yes. Searching "calc" will find all functions with "calc" anywhere in the name (like "calculate_total", "calculate_average", "recalculate"). Searching matches anywhere in the function name or file name.

Q: What's the difference between Search and Advanced Filters?
A: Search is for finding specific functions by name or file path. Advanced Filters are for categorizing functions by documentation status (has/no docstring, validation issues). Use Search for "find me this function" and Filters for "show me all functions like this".

Q: Can I search in docstring content?
A: No. Search only looks at function names and file paths, not the content of docstrings. To find content-specific issues, use the Validation tab.

Q: Why do I need to press Enter for the search to apply?
A: Pressing Enter prevents the app from updating the results with every keystroke you make. Type your full search term, then press Enter once to apply it. This makes the search faster and less resource-intensive.

Q: Can I use wildcards or regex in search?
A: No. Search is literal text matching only. Wildcards and regex patterns are not supported.

Q: If I search for "test", will it find a function called "test_module"?
A: Yes. Search matches "test" anywhere in the function name or file path, so "test_module", "my_test", "retest", and similar would all be found.

Q: Can I download search results like I can with filters?
A: Search results display in a table but don't have a dedicated download button. Use Dashboard > Export to generate a full report, or use Advanced Filters > Download Filtered Results for an equivalent download option.

Q: What if I search for something with zero matches?
A: The page shows an info message "No functions match the criteria." and the table remains empty. Try a broader search term.

[/SCREEN]

---

## [SCREEN: dashboard-tests]

**NAME:** Dashboard / Tests Sub-Tab

**DESCRIPTION:** Run or re-run the workspace test suite. Includes snapshot health tests plus AI-generated tests for your code. View pass/fail results, error diagnostics, and generated test code.

**ELEMENTS:**

- **Panel Header** — Icon (🧪) and title "Workspace Tests" with subtitle "Run static baseline suites plus AI-generated project suites with a consistent diagnostics and reporting layout."

- **Test Action Buttons** — One or two buttons depending on state:
  - On first run (no prior test results): Single button `▶️ Run Tests` (blue, full width).
  - After first run: Two buttons:
    - `▶️ Rerun Tests` — Re-execute all tests with cached results.
    - `🧨 Clear Cache` — Delete all cached test files and force full regeneration from scratch.

- **Test Summary Metrics** — 4 cards after tests complete:
  - Tests Run: Total number of tests executed.
  - Passed: Count of passing tests (green color).
  - Failed: Count of failing tests (red color).
  - Success Rate: Percentage of tests passed (green/yellow/red based on percentage).

- **Test Report Download** — `📥 Download Test Report (JSON)` button. Downloads full test results in JSON format. Visible after tests complete.

- **Test Results Chart** — Stacked bar chart showing pass/fail counts for each test suite (if tests have run). X-axis is test suite names (compressed to fit). Y-axis is test count. Bars are color-coded: green for passed, red for failed, stacked.

- **Test Group Headers** (after results): Two sections:
  - `🛡️ App Health Test Suites` — Snapshot tests built into the app (from the Test/ folder).
  - `🛠️ Project Code Tests` — AI-generated tests for your uploaded code (from workspace_tests/dynamic or workspace_tests/cached).

- **Test File Expanders** — For each test file, an expander showing:
  - File name and pass/fail counts (e.g., "✅ coverage_reporter — 12/12 Passed" or "❌ dashboard — 8/12 Passed").
  - When expanded, list of individual tests with icons:
    - 🟢 for passed tests.
    - 🔴 for failed tests.
  - For failed tests: simple explanation of the failure plus raw traceback.
  - View Generated Test Code section showing the actual AI-written test file code.

- **Skipped Files Notice** (if applicable) — Files with missing docstrings or parse errors are listed with ⚠️ or 🔴 icons and reasons:
  - "Missing docstrings (N/M documented)"
  - "Parser Error: ..."
  - "No functions found in file"
  - Includes a button "Fix now in DocStrings Tab ↗️" to navigate and fix.

**ACTIONS:**

- **Click Run Tests** → Full workspace scan begins. Files are written to workspace_context. Snapshot tests from Test/ are copied. AI tests are generated for documented files. Pytest is executed against both layers. Results are displayed when complete.

- **Click Rerun Tests** → If the workspace hasn't changed (same files, same fixes), an optimization shows a toast "🚀 Instant Re-run: No changes detected, reusing results." Results are shown immediately without re-running. If workspace has changed, full re-run occurs.

- **Click Clear Cache** → All cached AI test files are deleted. When you rerun, tests are regenerated from scratch (slower but fresh).

- **Click individual test expander** → Shows detailed pass/fail status for each test in that file plus error explanations for failures.

- **Click Fix now in DocStrings Tab** button → Navigates to DocStrings screen to generate missing docstrings.

**STATES:**

- **Never run:** Shows "Run tests to see summary, charts, and downloadable reports." Only single Run button is visible.

- **Tests running:** Progress bar shows current generation/execution status. Page is non-interactive during this time.

- **Tests complete:** Metrics, charts, and detailed results are fully visible.

- **All passed:** Green checkmarks and success message "All tests passed."

- **Some failed:** Red fail count prominent. Expanders show detailed error info for each failure.

- **Files skipped:** Skipped files list appears with explanations.

**TIPS:**

- The first test run may take longer because the app generates AI test code from scratch. Rerun is faster if nothing changed.

- If tests fail, expand the failing test file to see a human-readable explanation of what went wrong, plus the raw traceback.

- Use "Clear Cache" if results seem stale or if you've made major changes to your code and want a fresh test generation.

- Snapshot tests (App Health suites) validate the app itself. Project Code tests validate your uploaded files. If Health tests fail, there's a bug in the app. If Project tests fail, your code needs fixes.

- If a file is skipped because of "Missing docstrings", use the "DocStrings" tab to generate them, then rerun tests.

**KNOWN ISSUES:**

- Test collection may fail silently if imports are incorrect. The app attempts to normalize imports but may not catch all edge cases.

- AI test generation is best-effort and may not cover all edge cases in your code.

[/SCREEN]

---

## [SCREEN: dashboard-export]

**NAME:** Dashboard / Export Sub-Tab

**DESCRIPTION:** Generate downloadable reports of workspace metrics in multiple formats (JSON, Markdown, CSV, Plain Text). View a live preview before downloading.

**ELEMENTS:**

- **Panel Header** — Icon (📥) and title "Export Reports" with subtitle "Download a high-level docstring coverage report with overall metrics, file summaries, and simple function-level status."

- **Metric Cards** — 4 cards showing workspace totals:
  - Total Files
  - Total Functions
  - Has Doc String (count)
  - No Doc String (count)

- **Export Format Selector** — Dropdown menu with 4 options:
  - JSON
  - Markdown
  - CSV
  - Plain Text
  Default: JSON.

- **Download Button** — `⬇️ Download .{ext}` — Button reflects selected format (e.g., "Download .json"). Disabled if no functions exist.

- **Live Preview** — Code block below the download button showing the exact content that will be exported. Preview updates instantly when format changes.

**ACTIONS:**

- **Select an Export Format** → Preview updates to show the export in that format. Button label updates.

- **Click Download** → File is downloaded to your downloads folder with name format "dashboard_docstring_report.{ext}".

**STATES:**

- **No functions:** Info message "No functions found to export."

- **Format selected:** Preview shows export content. Download button is enabled.

- **Downloaded:** Browser handles file save. No confirmation in app.

**TIPS:**

- Use JSON format for programmatic integration or data analysis tools.

- Use Markdown format to create a readable report for documentation or GitHub wikis.

- Use CSV for importing into spreadsheets or data tools.

- Use Plain Text for simple, human-readable reports that don't need special formatting.

- The same report structure is available from individual file tabs (file-level export) and from the Metrics tab (workspace-level export). Export from Dashboard for a snapshot at any moment.

**KNOWN ISSUES:**


**KNOWN ISSUES:**

- None documented.

**FAQ:**

Q: What format should I choose for exporting?
A: JSON is best for programmatic analysis or as an archive. Markdown is ideal for human-readable documentation and team wikis. CSV works with Excel and other spreadsheet tools. Plain Text is simplest but less structured.

Q: Can I edit the report after exporting?
A: Yes, all exported files are standard formats. Edit Markdown in any text editor, JSON in code editors, CSV in Excel, and Plain Text anywhere. Changes won't affect your workspace analysis until you re-export.

Q: How is Export different from the Metrics screen?
A: Export creates snapshot reports at this moment. Metrics shows live statistics of your current workspace. Export is for sharing/archiving; Metrics is for monitoring trends and real-time status.

Q: Does the export auto-update if I change my code?
A: No. Exports are static snapshots at the time you click Download. If you change code or upload new files, run Export again to get an updated report.

Q: Can I export only certain functions or files?
A: No directly. Use Advanced Filters first to narrow your view, then the export will include all currently visible functions. This gives you flexible subset exporting based on your filter criteria.

Q: What information is included in each export?
A: All exports include function names, file paths, docstring status, validation results, docstring style (if applicable), and any error messages. Markdown includes formatting and structure. JSON includes all metadata. CSV includes all columns that fit the format.

Q: Can I share exported reports with team members who don't have access to this app?
A: Yes. Exported files are standard formats readable by any text editor or spreadsheet tool. Send the file directly; no app access needed to view it.

Q: What's the maximum file size for an export?
A: Exports are limited by your browser's download speed and system memory. Large workspaces (1000+ functions) may take 30+ seconds to generate. If export fails, reduce workspace size or generate smaller reports with filtered views.

[/SCREEN]

---

## [SCREEN: dashboard-help]

**NAME:** Dashboard / Help Sub-Tab

**DESCRIPTION:** Interactive guide to every feature in the app. Click any card to view detailed information about that feature.

**ELEMENTS:**

- **Panel Header** — Icon (💡) and title "Help & Guides" with subtitle "Open any dashboard tab card to view feature details and how-to steps."

- **Help Card Grid** — 3 columns of clickable cards. Each card represents a major feature or screen:
  - 🧭 Left Panel: Explorer
  - 🏠 Main Tab: Home
  - 🎛️ Main Tab: Dashboard (Overview)
  - 🔎 Dashboard Tab: Advanced Filters
  - 🔍 Dashboard Tab: Search
  - 🧪 Dashboard Tab: Tests
  - 📤 Dashboard Tab: Export
  - 💡 Dashboard Tab: Help
  - ✅ Main Tab: Validation
  - 📝 Main Tab: DocStrings
  - 📈 Main Tab: Metrics
  - 📄 File Tabs (Opened Files)
  Cards have a glass effect and glow on hover.

- **Selected Card Detail View** — After clicking a card, a panel expands (or modal opens if supported by Streamlit version) showing:
  - **Features** section with bullet points listing what the card is for.
  - **How to Use** section with step-by-step instructions.
  - **Close** button to dismiss the detail view.

**ACTIONS:**

- **Click any Help card** → Detail view appears showing Features and How to Use guidance.

- **Click Close button** → Detail view closes. Card grid returns.

- **Click another card while one is open** → New card's content replaces the previous one.

**STATES:**

- **Default:** Card grid is visible. No detail view is selected.

- **Card selected:** Detail view appears below or as modal. Card highlighting indicates which is selected.

- **Help closed:** Returns to card grid.

**TIPS:**

- Use this tab anytime you need a quick reference on how a feature works.

- Cards are organized by the screens/sections they explain, so you can find guidance for exactly where you are in the app.

- Features bullet points summarize what a feature does. How to Use bullet points give steps to accomplish a task.

**KNOWN ISSUES:**


**KNOWN ISSUES:**

- None documented.

**FAQ:**

Q: Where do I find help if I'm stuck?
A: Click the "Dashboard > Help" tab. The entire tab is searchable documentation. For quick answers, search the Help tab directly. For more complex issues, check Troubleshooting section in this Knowledge Base.

Q: Can I search within the Help tab?
A: Yes. There's a search box at the top of the Help tab. Type your question or keyword and matching help articles appear instantly.

Q: What if I can't find the answer to my question?
A: The Help tab covers all major features. If your issue isn't documented, it might be a bug or edge case not yet covered. Report the issue through GitHub or contact support.

Q: Can I print the help documentation?
A: Yes. Click the print icon in the Help tab header or use your browser's Print function (Ctrl+P / Cmd+P). The help content will print in readable format.

Q: Can I keep the Help tab visible while working on other tabs?
A: The Help tab works like any other tab. You can keep it open and switch between tabs to reference help while working. Help context doesn't disappear when you switch tabs.

Q: Does this app update the help docs automatically?
A: Help documentation is bundled with the app. When you update the app, help is updated automatically. Check the main app README for what's new in each version.

Q: Who maintains this Help documentation?
A: The help section is maintained by the core app developers and updated with each release. Feedback helps improve the documentation. Report typos, unclear explanations, or missing topics through GitHub.

Q: Can I access Help if I'm offline?
A: Yes. Help documentation is built-in. You don't need internet to access it. The entire Help tab works offline.

[/SCREEN]

---

## [SCREEN: validation-screen]

**NAME:** Validation Screen

**DESCRIPTION:** Check docstring quality against PEP 257 standards and parameter documentation accuracy. View errors by file and apply AI fixes. Features auto-generated charts and detailed error listings.

**ELEMENTS:**

- **Screen Header** — Icon (✅) and title "Validation" in a frosted glass container.

- **Error Distribution Charts** (if files are fully documented):
  - **Pie Chart** (left) — Shows error code distribution. Each error type is a slice, color-coded. Labeled with error code and percentage. Title: "Errors by Rule Type". Hole in the middle (donut style).
  - **Bar Chart** (right) — Shows errors per file. File names on X-axis (compressed to fit). Error count on Y-axis. Title: "Errors by File".
  - If all files are clean, charts show "No errors found to chart." and "All files are clean."
  - If any file is incomplete (has functions but not all documented), a warning appears instead: "📝 Generate docstrings to validate. Some files are incomplete, so validation graphs are hidden until all functions are documented."

- **Validation Navbar** — Frosted glass bar with:
  - `📋 Files & Validation Breakdown` text label (left).
  - `🔧 Fix All with AI (N files)` button (right, only if N files have fixable errors). Clicking this runs AI fixes on all error-containing files in parallel.

- **File Expanders** — One expander per file:
  - Icon (✅ for clean, 🔴 for errors) and file name.
  - Pass/fail status (e.g., "0 Rules Broken" or "12 Rules Broken").
  - Tag "🟢 Fixed" if file was already fixed by AI and has no remaining errors.
  - When expanded:
    - If no errors: Success message "All functions comply!"
    - If errors: List of broken rules per function. Each error shows:
      - Function name.
      - Line number of the error within the docstring.
      - Error code (e.g., "D200", "D401", "DAR101").
      - Human-readable message describing the violation.
    - Model selector dropdown: "Choose an AI Model to fix this file" (allows per-file model override).
    - `🔧 Fix {filename} with AI` button — Runs AI fix on that file only.
    - After fix: Diff pills showing lines added/modified and lines removed.

- **Skipped Files** (if applicable):
  - Some files may be skipped if they have no docstrings to validate. Shows ⚠️ icon and explanation.
  - Skipped files are not included in error charts.

**ACTIONS:**

- **Click a File Expander** → Shows detailed error breakdown for that file.

- **Select a Model from the Model Dropdown** → Changes which AI model will perform the fix for that file.

- **Click Fix {filename} with AI** → Runs AI fix on that single file. Spinner shows "🤖 AI is fixing...". After complete, file is updated with fixed docstrings. Re-parsing occurs and tests are regenerated if the file is now fully documented.

- **Click Fix All with AI** → Runs AI fixes on all files with errors in parallel. Progress bar shows current status.

**STATES:**

- **Incomplete files:** Warning appears "📝 Generate docstrings to validate..." Charts are hidden. Files show SKIPPED status with "No docstrings to validate" message.

- **No files uploaded:** Info message "No files uploaded."

- **Parse error:** Expander shows "Parse Error" with error message.

- **Clean file:** ✅ icon. "All functions comply!" message inside.

- **File has errors:** 🔴 icon. Error count shown. Expander lists detailed errors.

- **File is fixed:** 🟢 tag next to file name. Shows "All issues fixed by AI!"

**TIPS:**

- You can only validate and fix files that are fully documented (all functions have docstrings). If a file is incomplete, go to DocStrings tab to generate missing docstrings first.

- Validation errors are driven by two standards:
  - **PEP 257 style violations** (D200, D400-D415, D205, D212, D300, D412, D413): Formatting and structure issues like missing summary lines, imperative mood violations, and quote style.
  - **Parameter documentation (DAR codes)** (DAR101, DAR201, DAR301): Missing Args, Returns, or Raises sections in docstrings.

- The AI fix is smart but not perfect. Always review generated docstrings to ensure they're accurate.

- You can fix all files at once using "Fix All with AI" or fix them one at a time to have more control.

- Use per-file model selection to try different models on tricky files if one model's fixes aren't satisfactory.

- Detailed explanations of every error code are available in the Validation screen FAQ (hover or click the question mark icon).

**KNOWN ISSUES:**


**KNOWN ISSUES:**

- Mixed-style files may produce validation errors because some tools don't recognize all docstring formats. Use the Style Converter to normalize to one style first.

**FAQ:**

Q: Why does it say my files are skipped?
A: Files are skipped if they have incomplete docstrings (not all functions are documented). Validation only works on fully documented files. Go to DocStrings tab to generate missing docstrings first.

Q: What do the error codes like D200 and D401 mean?
A: These are PEP 257 docstring style codes and Darglint parameter documentation codes. The Validation screen FAQ now includes detailed explanations for all supported error codes (D200, D400-D415, DAR101, DAR201, DAR301, etc.). See the in-app FAQ on the Validation screen for complete error code reference.

Q: How long does it take to fix a file with AI?
A: Typically 5-20 seconds per file, depending on file size and AI model speed. Large files may take longer. You can monitor progress with the "AI is fixing..." spinner.

Q: Can I fix individual rules or do I have to fix the whole file?
A: You must fix the whole file at once through the UI. The AI reads all errors and fixes them together. If you want finer control, download the file, edit manually, and re-upload.

Q: Can I override the AI model for a single file?
A: Yes. Each file has its own model dropdown. Select a different model before clicking "Fix {filename}" and that model will be used just for that file.

Q: Can I undo a fix if the AI gets something wrong?
A: No direct undo in the app, but the original file is preserved. Re-upload the original if needed. Always review AI changes before committing to your codebase.

Q: Why do some files show error charts and others don't?
A: Error charts only appear when all files are fully documented. If some files are incomplete (missing docstrings), validation charts are hidden until you generate those missing docstrings.

Q: Can I validate only certain files or must I validate everything?
A: Validation runs on all uploaded files. To focus on specific files, deselect others in the Sidebar, then validation and fixing will only apply to the selected files.

Q: What should I do after the AI fixes validation errors?
A: Review the changes carefully—check the diff pills to see what was modified. Read the fixed docstrings to ensure they match your actual function logic. Then commit the changes to your repository.

Q: Why did the AI fix fail for my function?
A: Common causes: API quota exceeded, network interrupted, or the function code is too complex for the AI. Wait a few minutes and retry, or try a different AI model.

[/SCREEN]

---

## [SCREEN: docstrings-screen]

**NAME:** DocStrings Screen

**DESCRIPTION:** Convert docstrings between styles (Google, reST, NumPy) or generate missing docstrings using AI. Includes side-by-side preview, diff view, apply/download/copy actions.

**ELEMENTS:**

- **Screen Header** — Icon (📝) and title "DocStrings" in frosted glass container.

- **File Selector** — Large dropdown showing all uploaded files. Required to select before any other actions. Label: "Select File".

- **Style Detection Card** — Shows the detected docstring style in the selected file:
  - Icon (colored, matches style):
    - 🟡 for Google
    - 🔵 for reST
    - 🟣 for NumPy
    - 🔀 for Mixed
    - ⚠️ for None/Incomplete
  - Style name and count (implied by the color).
  - Border color matches the style color for visual consistency.

- **Docstring Status Legend** — An `info` alert if no docstrings are detected:
  - Text: "⚠️ No complete docstrings detected. You can generate them using AI."
  - Switches interface to "Generate" mode (see below).

- **Control Row (if docstrings exist — Conversion Mode)**:
  - **Scope Selector** — Dropdown with options:
    - "📄 Whole File" — Converts entire file.
    - "⚙️ {function_name}" — Converts a specific function. One option per function.
    Default: "📄 Whole File".
  - **Target Style Selector** — Dropdown with available target styles (excludes the detected style):
    - If detected is Google, options are "reST" and "NumPy".
    - If detected is reST, options are "Google" and "NumPy".
    Etc.
  - **Convert Button** — `⚡ Convert` button (blue, type="primary"). Triggers conversion.
- **Control Row (if no docstrings — Generation Mode)**:
  - **Model Selector** — Same as conversion mode.

    **TIPS:**

    - Generation is smarter than conversion because it rewrites from scratch. Consider generating rather than converting if results are poor.

    - Use per-function conversion (Scope = single function) to fix just one function without risking others.

    - Always review the diff before applying conversions to multi-function files.

    - Different AI models may produce different docstring quality. Try multiple models if unsatisfied.

    **FAQ:**

    Q: What's the difference between Conversion and Generation?
    A: Conversion changes existing docstrings from one style to another (Google → NumPy). Generation creates brand-new docstrings from scratch for functions that have none. Generation is more flexible but requires no pre-existing docstrings.

    Q: What are the three docstring styles this app supports?
    A: Google style (keyword-based), reST style (markup-based), and NumPy style (name-based sections). All three are equally valid; choose based on your team's preference or project standards.

    Q: How does the app know what style my docstrings are in?
    A: It analyzes the format and structure of existing docstrings. Google uses "Args:", "Returns:"; reST uses `:param:`, `:returns:`; NumPy uses indented sections under "Parameters", "Returns". Mixed means multiple styles detected.

    Q: What if my file has no docstrings at all?
    A: Use Generation mode. Select your target style and click Generate. The AI will create docstrings from scratch for all functions based on their signatures and code.

    Q: Can I convert just one function in a file?
    A: Yes. Use the Scope Selector and choose a specific function name. Only that function's docstring will be converted; others remain unchanged.

    Q: What should I do if the conversion looks wrong?
    A: Click Dismiss to discard. The conversion uses a preview, so nothing is applied yet. You can try again with a different model or manually edit the docstrings.

    Q: Are complex type hints handled correctly?
    A: Usually, but not always. Union types, Generics, and other complex hints may not convert perfectly. Review the diff before applying, especially for complex code.

    Q: Can I revert a conversion I applied?
    A: No built-in undo. Re-upload the original file from version control, or use Conversion again to convert back (though this may not restore perfectly).

    ---
  - **Left Column:** `🔵 Current Code` — Code block showing original code (or the scoped function if not whole file).
  - **Right Column:** `🟢 {Target Style} Style` — Code block showing AI-generated/converted code.
  - Both columns scroll independently (height 500px fixed).
  - Side-by-side comparison up to 500px height.

- **Action Row** (below preview, appears after conversion/generation):
  - **Apply Button** (`💾 Apply`) — Saves the converted code to the workspace. Updates the file's parsed results. Dismisses the preview.
  - **Dismiss Button** (`❌ Dismiss`) — Closes the preview and discards changes. No file is modified.
  - **Copy Button** (`📋 Copy`) — Copies the right-side code to clipboard via JavaScript injection. Shows toast "✅ Copied to clipboard!"
  - **Download Button** (`⬇️ Download`) — Downloads the right-side code as a `.py` file. File name includes target style (e.g., "myfile_google.py").

- **Diff Expander** (appears after preview, expanded by default):
  - Title: `🔍 Changes`
  - Shows unified diff format (standard `diff -u` output with `+++`, `---`, `@@` markers).
  - Scrollable code block (height 500px) if diff is large.
  - Shows "No changes detected." if input and output are identical.

**ACTIONS:**

- **Select a File** → Shows detected style for that file. If file has docstrings, shows Conversion Mode. If no docstrings, shows Generation Mode.

- **Conversion Mode: Choose scope and target style, click Convert** → Spinner shows "🔄 Converting to {style} style…". After success:
  - Preview shows current code (left) and converted code (right).
  - Diff expander shows what changed.
  - Action buttons become available.

- **Generation Mode: Choose style, click Generate** → Spinner shows "✨ Generating {style} docstrings…". Works like Conversion.

- **Click Apply** → Converted code replaces file's current version. New tests are generated if applicable. Toast shows "✅ Applied to source code and cached tests!". Preview closes.

- **Click Dismiss** → Preview closes without applying. Changes are discarded.

- **Click Copy** → Right-side code is copied to system clipboard. Toast confirms.

- **Click Download** → Right-side code is downloaded as `.py` file.

**STATES:**

- **File Selected, No Docstrings:** Generation Mode is shown.

- **File Selected, Has Docstrings:** Conversion Mode is shown.

- **Conversion/Generation Running:** Spinner overlay. UI is blocked.

- **Preview Open:** Apply/Dismiss/Copy/Download buttons are visible. Diff is shown. Scope/Style/Model selectors are disabled.

- **Preview Dismissed:** Selectors are enabled again. Preview and action buttons hide. Diff hides.

- **Applied:** File is updated. "Analyzing..." message may appear briefly as file is re-parsed and tests regenerate. Page reruns.

**TIPS:**

- **Generate first:** If your file has no docstrings, use Generate mode to create them in your desired style all at once.

- **Convert second:** If you want to switch styles (e.g., from Google to NumPy), use Conversion mode.

- **Mixed styles:** If your file mixes styles, use Generation mode to replace all docstrings with a consistent style.

- **Per-function conversion:** Use the Scope selector to convert just one function if others are already correct. Useful for iterating on specific functions.

- **Review the diff:** Always check the diff before applying to ensure the AI-generated docstrings are semantically correct.

- **Download before apply:** If you want to review the code outside the app, download it and verify, then paste it back in and apply.

**KNOWN ISSUES:**



**KNOWN ISSUES:**

- Generation can hallucinate docstring content if function signatures are ambiguous. Always review before applying.

- Style conversion may not be 100% perfect for edge cases (e.g., complex nested type hints). Manual review recommended.

**FAQ:**

Q: What's the difference between "Generate" and "Convert"?
A: Generate creates brand-new docstrings from scratch for functions that have none. Convert takes existing docstrings and changes them from one style (Google) to another (NumPy, reST). Use Generate if no docstrings exist; use Convert to change the style.

Q: Can I convert just one function in a file instead of the whole file?
A: Yes. Use the Scope Selector dropdown. Select the specific function name and only that function will be converted. Other functions stay unchanged. This is useful for iterating on specific functions.

Q: What does "Mixed" style mean?
A: Mixed means your file contains docstrings in multiple styles (some Google, some reST, etc.). To clean this up, select "Whole File" and choose a target style to make all docstrings consistent.

Q: How does the app detect the docstring style?
A: The app analyzes the format of existing docstrings (structure, keywords, indentation) and matches them to the known patterns for Google, reST, and NumPy. Mixed means multiple patterns were found.

Q: Can I preview the converted code before applying it?
A: Yes. After clicking Convert, the preview shows the current code on the left and the target-style code on the right. Review both before choosing to Apply, Dismiss, Copy, or Download.

Q: What happens when I click "Apply"?
A: The converted docstrings replace the originals in your workspace. Your file is immediately updated. Tests are regenerated if the file is now fully documented. You can't undo—review carefully before applying.

Q: Should I review generated docstrings?
A: Yes, always. AI sometimes makes assumptions or hallucinates details, especially for complex functions. Read the generated docstrings to ensure they match your actual function logic and parameters.

Q: Can I edit a generated docstring before applying?
A: Not directly in the preview. Copy the code, paste it into a text editor, make edits, then you can download the modified file. Apply is all-or-nothing—you apply the entire generated preview.

Q: Can I revert a style conversion if I change my mind?
A: No built-in undo. If you want to revert, re-upload the original file from your version control system, or use Convert again with the previous style selected (though this may not perfectly restore).

Q: Why does it show "No changes detected"?
A: This means the AI determined your docstrings are already in the target style or don't need modification. The current and generated versions are identical. This is normal if you've already converted or if the conversion makes no changes.

[/SCREEN]

---

## [SCREEN: metrics-screen]

**NAME:** Metrics Screen

**DESCRIPTION:** Workspace-wide export and reporting. Choose export format (JSON, Markdown, CSV, Plain Text) and download a comprehensive analysis of all files and functions.

**ELEMENTS:**

- **Screen Header** — Icon (📈) and title "Metrics" in frosted glass container.

- **Export Format Selector** — Dropdown with 4 options:
  - JSON
  - Markdown
  - CSV
  - Plain Text

- **Metric Cards** (optional, may be shown on metrics page before export) — Shows summary counts if desired.

- **Download Button** — `⬇️ Download as .{ext}` — Button label reflects selected format. Downloads report with file name "code_review_report.{ext}".

- **Live Preview** — Code block showing exact export content in selected format. Updates instantly when format changes.

**ACTIONS:**

- **Select Export Format** → Preview updates. Button label changes.

- **Click Download** → Report file is downloaded.

**STATES:**

- **Format selected:** Preview and download button available.

- **Downloaded:** Standard browser file download behavior.

**TIPS:**

- Metrics tab is similar to Dashboard / Export but provides workspace-wide reporting with slightly different organization. Use whichever feels natural for your workflow.

- Metrics are most useful for final reporting after you've completed all fixes and validation.

**KNOWN ISSUES:**


**KNOWN ISSUES:**

- None documented.

**FAQ:**

Q: Is the Metrics screen the same as Dashboard / Export?
A: Similar but slightly different. Both give you workspace overview exports. Dashboard/Export is a snapshot tab. Metrics is the dedicated reporting screen. Use whichever feels natural for your workflow—both produce identical reports.

Q: What information is included in the metrics report?
A: All reports include: file names, function counts, documentation status for each function, validation errors, docstring styles detected, and file-by-file analysis. The exact format depends on your export choice (JSON, Markdown, CSV, or Plain Text).

Q: Can I schedule metrics to be generated at a certain time?
A: No. Metrics are generated on-demand when you click Download. To track trends over time, you'd need to manually download reports and compare them.

Q: Can I compare metrics from two different time periods?
A: No built-in comparison feature. Download reports from different dates, then compare them manually in Excel or a text editor to track changes in documentation coverage.

Q: Do the metrics include validation errors from the Validation screen?
A: Yes. If files have validation errors, those are included in the report. The exact level of detail depends on your format choice (JSON has most detail, Plain Text has less).

Q: Can I export just the metrics without function-level details?
A: No. Exports include all details. To export a summary-only, download as Plain Text—it's the most concise option.

Q: What tests are included in the metrics report?
A: Test counts and status are included for reporting purposes. If a function has AI-generated tests, that status is reported. Actual test code isn't included in the metrics export, only TestStatus.

Q: How often should I generate fresh metrics?
A: Generate metrics whenever you've made significant changes: after fixing docstrings, after running validation, or periodically for monitoring. Each download captures the current state of your workspace.

Q: Can I see metrics for just one file?
A: No. Metrics tab exports your entire workspace. For single-file metrics, open that file's tab (File Tab screen) where file-level stats are shown.

Q: What's the file size of a typical metrics export?
A: Depends on workspace size. 50 functions ≈ 50KB. 500 functions ≈ 500KB. If export is too large, try exporting CSV or Plain Text (smaller than JSON).

[/SCREEN]

---

## [SCREEN: file-tab]

**NAME:** Individual File Tab (Opened From Sidebar)

**DESCRIPTION:** Editor view for a single file. Shows current code, function breakdown, metrics, and per-file export options. Accessed by clicking a file name in the sidebar or opening a file from another screen.

**ELEMENTS:**

- **File Header Panel** — Styled container with:
  - Left side: Large file name (compressed with ellipsis if too long).
  - Right side: Two buttons:
    - **Close File** — Removes this file's tab but keeps it in sidebar. File is not deleted.
    - **Delete File** — Removes file from workspace entirely. Tab closes and file is deleted from sidebar.
    Both buttons have yellow and red hover effects respectively.

- **Metrics Cards Row** — 4 cards showing file-level statistics:
  - Total Functions: Count of functions in this file.
  - Documented: Count with docstrings (green).
  - Undocumented: Count without docstrings (red).
  - Coverage: Percentage or "N/A".

- **Current Code Section**:
  - Header: "📄 Current Code" or "✨ Current Code (AI Fixed)" if file was modified by AI fixes.
  - If fixed: Two diff pills showing "+ N lines added/modified" and "− N lines changed".
  - Code block showing the current source (original or AI-fixed version).
  - **Download Button** — `⬇️ Download` — Downloads current code. File name is "filename.py" or "fixed_filename.py" if fixed.
  - **Copy Button** — `📋 Copy` — Copies code to clipboard via JavaScript.

- **Function Breakdown Section**:
  - Title: "🔍 Function Breakdown"
  - If zero functions: Info message "No Functions found."
  - If functions exist: Expander per function showing:
    - Icon (✅ or ❌) indicating if documented.
    - Function name and line range.
    - When expanded:
      - Function metadata: name, start line, end line, has docstring (Yes/No).
      - If it has a docstring: Docstring content displayed in a code block.

- **Export Section**:
  - Title: "📥 Export {filename} Report"
  - Prompt: "Choose export type:"
  - Dropdown selector with 4 format options: JSON, Markdown, CSV, Plain Text.
  - Download button: `⬇️ Download {filename} Report as .{ext}` — Downloads file-specific report.
  - Live Preview code block showing export in selected format.

**ACTIONS:**

- **Click Close File** → Tab for this file closes. File remains in sidebar. Other open tabs shift position.

- **Click Delete File** → Confirmation (implicit via button action). File is deleted from workspace. Tab closes. Sidebar refreshes.

- **Click Download (Current Code)** → Code is downloaded.

- **Click Copy (Current Code)** → Code is copied to clipboard. Toast confirms.

- **Click Function Expander** → Function details expand, showing metadata and docstring if present.

- **Change Export Format** → Live Preview updates to show export in new format.

- **Click Download Report** → File-specific report is downloaded in selected format.

**STATES:**

- **File Opened:** Tab is visible and active. File name appears in tab bar. Content loads and displays.

- **File AI-Fixed:** "✨ Current Code (AI Fixed)" label appears. Diff pills show change statistics.

- **File Closed:** Tab disappears but file remains in sidebar.

- **File Deleted:** Tab disappears. File is removed from sidebar and workspace entirely.

- **Export Format Selected:** Download button and preview are ready.

**TIPS:**

- Use File tabs to inspect specific files in detail. Open multiple files in different tabs to compare them side-by-side (tabs appear in the tab bar).

- The "Close File" button is useful for cleanup—it removes the tab without deleting the file. Use "Delete File" only when you're sure you want to remove the file from the entire workspace.

- Per-file export is useful when you want a detailed report on just one file to share with a colleague.

- Check the diff pills after AI fixes to understand what the AI changed in your file.

**KNOWN ISSUES:**


**KNOWN ISSUES:**

- None documented.

**FAQ:**

Q: What's the difference between "Close File" and "Delete File"?
A: Close File removes the tab (you won't see it open) but keeps the file in the sidebar. Delete File removes the file completely from your workspace and sidebar. Use Close for temporary cleanup; use Delete to remove unwanted files permanently.

Q: What does "AI Fixed" mean in the file tab title?
A: If the file was processed by Validation > Fix All or Fix {filename}, it shows "AI Fixed". This means the AI modified the docstrings. Check the diff pills (showing lines added/removed) to see what changed.

Q: Can I see what the original code looked like before AI fixed it?
A: Yes. The diff pills show summary statistics. For full details, re-upload the original file from your git repository or backup, then compare side-by-side in two tabs.

Q: What do the diff pills show?
A: Two pills appear: green pill shows "+ N lines added/modified" and red pill shows "− N lines removed". These indicate the scope of AI changes to the docstrings.

Q: Can I verify the fix is correct before committing to my repo?
A: Yes. Review the code in the Current Code section. Copy it (📋 Copy), paste into a temporary file, and verify it's correct. If satisfied, use Download to save it, then commit to your repo.

Q: Can I edit the code directly in the file tab?
A: No. The file tab is read-only. If you need to edit manually, Download the code, edit it locally, then re-upload the modified version.

Q: Can I export or download just the docstrings from this file?
A: You can download the entire file (📄 Current Code section). For just a report, use the Export Report section at the bottom to generate a file-specific report in JSON/Markdown/CSV/Plain Text format.

Q: How is the per-file export different from workspace-level export?
A: Per-file export shows only this file's functions and their status. Workspace export (from Metrics or Dashboard/Export) shows all files. Use per-file for focused reports to share with a colleague about one file.

Q: Can I have multiple files open in tabs at the same time?
A: Yes. Clicking multiple files from the sidebar opens them in different tabs. You can switch between tabs to compare files side-by-side or work on multiple files sequentially.

Q: What happens to this tab if I delete the file?
A: The tab closes immediately. The file is removed from the workspace and sidebar. If you need it back, re-upload the original from your backup or version control system.

[/SCREEN]

---

## [SIDEBAR]

**NAME:** Left Sidebar (Explorer Panel)

**DESCRIPTION:** Fixed left panel always visible. Contains navigation, AI model selector, file uploader, and file list management.

**ELEMENTS:**

- **Explorer Header** — Text "📂 Explorer" in a styled label. Marks the start of sidebar content.

- **Navigation Section**:
  - Label: "Navigation"
  - Selectbox with 5 options:
    - 🏠 Home
    - 🎛️ Dashboard
    - 📝 DocStrings
    - ✅ Validation
    - 📈 Metrics
  - Selecting an option switches to that screen. Dashboard is automatically added to the tab bar even if not open yet.

- **AI Fix Model Section**:
  - Label: "Choose AI Fix Model"
  - Selectbox with available AI models (e.g., GPT-4, Claude, etc.). Shows friendly names.
  - Selected model is used by default for all AI fixes and generations.
  - Can be overridden per-file in Validation tab.

- **Add Files Section**:
  - Label: "Add Files"
  - File uploader accepting `.py` and `.zip` files.
  - Styled with yellow dashed border.
  - When new files are selected and uploaded: "Analyzing Workspace... Please wait." spinner. Files are processed and added to the workspace. Sidebar refreshes to show new files.

- **File List Section**:
  - Label: "Files"
  - If no files: Info message "No files in workspace."
  - Per file: Horizontal row with 3 columns:
    - **Left (wider column):** Clickable button showing `📄 {compressed name}`. Tooltip shows full file name. Click to open file in a new tab.
    - **Middle column:** Download icon button. Downloads current version of file (or AI-fixed version if available). Icon is hidden but functionality is via CSS bootstrap icon.
    - **Right column:** Trash icon button. Click to delete file from workspace. Confirmation is implicit (no modal).

**ACTIONS:**

- **Click Navigation selectbox** → Choose a destination screen. Page switches to that screen. If it's Dashboard, the dashboard tab opens.

- **Change AI Fix Model** → Model selection updates globally. Affects all subsequent AI operations until changed again.

- **Upload files via Add Files uploader** → New files are processed. Sidebar updates to include them in the file list.

- **Click file name button** → File tab opens. If already open, focus switches to its tab.

- **Click download icon (middle column)** → File is downloaded.

- **Click trash icon (right column)** → File is deleted. No confirmation modal (relying on button press as confirmation).

**STATES:**

- **Empty workspace:** File list shows "No files in workspace." Navigation is available but most screens will show "Upload files first" messages.

- **Files loaded:** File list shows all uploaded files with action buttons.

- **File open:** File list shows the currently open file highlighted or bolded.

**TIPS:**

- Use the sidebar to quickly switch between screens without relying on the tab bar.

- Set your preferred AI model in the sidebar once. You can still override it per-file in the Validation tab if needed.

- The sidebar is always visible. You cannot collapse it in this version (buttons with collapse functionality are hidden via CSS).

- Use Add Files to add more files after initial upload. Processing is quick for individual files.

- Download from the file list if you want the current version of a file without opening the full file tab.

**KNOWN ISSUES:**


**KNOWN ISSUES:**

- Sidebar width is fixed and may truncate very long file names. File list buttons show full name on hover via tooltip.

**FAQ:**

Q: Can I collapse or hide the sidebar to get more screen space?
A: No. The sidebar is fixed and always visible in this version. There's no collapse button to hide it. You get full use of it to navigate and select files.

Q: How do I navigate to different screens in the app?
A: Use the Navigation dropdown in the sidebar. It shows all 5 screens (Home, Dashboard, DocStrings, Validation, Metrics). Select one to switch to that screen instantly.

Q: What happens if I change the AI Fix Model in the sidebar?
A: This changes the global model selection for all AI operations (fixes, generations, conversions). All subsequent AI tasks use the new model. You can still override it per-file in the Validation tab for specific files.

Q: Can each file use a different AI model?
A: Not by default. The sidebar model is global. But in the Validation tab, you can select a different model just for that file before clicking "Fix {filename}". This is a per-file override.

Q: What file formats can I add to my workspace?
A: Only `.py` (Python) and `.zip` files. The uploader has a yellow dashed border. Zip files are automatically extracted; Python files are added directly.

Q: Why is the file list showing very long names truncated?
A: The sidebar has fixed width. Long file names are compressed. Hover your cursor over a truncated name to see the full path in a tooltip.

Q: Can I reorder files in the file list?
A: No. Files are listed in the order they were uploaded. To change order, delete unwanted files or re-upload in the desired order.

Q: Can I download a file directly from the sidebar file list?
A: Yes, there's a download icon (middle column) next to each file name. Click it to download the current (or AI-fixed) version without opening the file tab.

Q: How do I delete a file from the workspace?
A: Click the trash icon (right column) in the file list. There's no confirmation modal—the file is deleted immediately. To recover, re-upload from your backup or version control system.

Q: Can I search the file list to find a specific file?
A: No built-in search in the sidebar. If you have many files, scroll through the file list or hover/read tooltips to find the one you want.

[/SIDEBAR]

---

## [CROSS_FEATURE: ai-docstring-fixing]

**NAME:** AI Docstring Fixing

**APPEARS IN:** Validation Screen, Dashboard / Tests (skipped files), File Tabs

**DESCRIPTION:** AI rewrites or fixes docstrings in your code. Can fix individual files or all flagged files at once. AI detects docstring style and rewrites to match.

**HOW IT WORKS:**

1. **Trigger:** Click `🔧 Fix {filename} with AI` in Validation tab, or `🔧 Fix All with AI` to fix multiple files at once.

2. **Model Selection:** Choose which AI model to use (dropdown in Validation tab, or global default from sidebar). Different models may produce different quality results.

3. **Execution:** AI analyzes the file and generates corrected docstrings. Process includes:
   - Parse current docstring style (Google, reST, NumPy, Mixed, or None).
   - Identify functions with missing or broken docstrings.
   - Generate fixes matching the detected style (or default to Google if no style found).
   - Replace docstrings in the file.

4. **Result:** Fixed file replaces original in workspace. File is re-parsed to update metrics. If fully documented, AI tests are regenerated (or cached tests are used).

5. **Diff:** After fix, two diff pills appear showing lines added/modified and lines removed.

**EDGE CASES:**

- **Mixed styles:** If file has mixed docstring formats, the AI uses the most common style as the target. Use DocStrings screen to normalize first for best results.

- **Undocumented functions:** If a function has zero docstring, the AI generates one from scratch based on the function signature and logic (may hallucinate details).

- **Complex code:** AI may struggle with very complex or ambiguous function signatures. Always review generated docstrings.

- **Large files:** Fixing large files may time out or produce inconsistent results. Consider fixing smaller sections.

- **No errors:** If a file already has valid docstrings, running Fix will skip it (no changes needed).

**TIPS:**




**TIPS:**

- Always review AI-generated docstrings before applying. They are best-effort and may not capture all nuances.

- Use per-file model selection to try different AI models if results are unsatisfactory.

- Fix All is faster if you have dozens of files—it runs in parallel. Single file fix is slower but gives more control.

**FAQ:**

Q: What exactly does AI Docstring Fixing do?
A: It analyzes your code and automatically rewrites or fixes docstrings to meet PEP 257 standards. It detects what style your docstrings are in (Google, reST, NumPy) and maintains that style when fixing.

Q: Where can I trigger AI Fixing?
A: In the Validation screen by clicking "Fix {filename} with AI" (single file) or "Fix All with AI" (all files at once).

Q: Why is reviewing the results important?
A: AI is powerful but not perfect. It may misunderstand complex function logic or make incorrect assumptions about parameters. Always read the fixed docstrings to verify accuracy before committing.

Q: What happens if my file has mixed docstring styles?
A: The AI detects the most common style and uses that for all fixes. For best consistency, use the DocStrings screen to convert all docstrings to one style first.

Q: Can the AI generate docstrings from scratch for undocumented functions?
A: Yes, if a function has no docstring at all, the AI will generate one based on the function signature and code logic. Always review these since AI can hallucinate details.

Q: Do large files take longer to fix?
A: Yes. Large files or files with complex code may take longer to process. If fixing times out or produces odd results, try fixing smaller files individually instead of all at once.

Q: If I click"Fix All", does it run on all files at once?
A: It runs in parallel (multiple files simultaneously), so it's much faster than fixing files one-by-one. However, it may be limited by API rate limits.

Q: What if a file already has valid docstrings?
A: The fix operation will skip it (no changes made). This is normal and expected; there's nothing to fix.

[/CROSS_FEATURE]

---

## [CROSS_FEATURE: docstring-style-conversion]

**NAME:** Docstring Style Conversion and Generation

**APPEARS IN:** DocStrings Screen, Home (style detection), Validation (style-aware fixes)

**DESCRIPTION:** Convert docstrings between three major styles (Google, reST, NumPy) or generate missing docstrings in your preferred style.

**HOW IT WORKS:**

1. **Detect:** App automatically detects the docstring style in your file when you select it in the DocStrings screen.

2. **Choose Mode:**
   - If file has docstrings: Conversion mode. Select target style and scope (whole file or single function).
   - If file has no docstrings: Generation mode. Select target style.

3. **Convert/Generate:** Click the appropriate button. AI processes the file.

4. **Review:** Side-by-side preview shows original (left) and result (right). Diff view shows exact changes.

5. **Apply or Discard:** Click Apply to save, or Dismiss to discard.

**EDGE CASES:**

- **Mixed styles:** If file contains multiple styles, detection shows "Mixed". App treats this as needing normalization. Use Generation mode to rewrite all docstrings in a single style.

- **None/Incomplete:** If file has no docstrings or only partial ones, detection shows "None/Incomplete". Use Generation mode.

- **Complex types:** Some type hints (especially Union, Generic, etc.) may not convert perfectly. Manual review recommended.

- **Parameter names:** If parameter names in docstrings don't match function signature, AI will fix them.

**TIPS:**

- Generation is smarter than conversion because it rewrites from scratch. Consider generating rather than converting if results are poor.

- Use per-function conversion (Scope = single function) to fix just one function without risking others.

- Always review the diff before applying conversions to multi-function files.

- Different AI models may produce different docstring quality. Try multiple models if unsatisfied.

[/CROSS_FEATURE]

---

## [CROSS_FEATURE: test-generation-and-validation]

**NAME:** Test Generation and Validation

**APPEARS IN:** Dashboard / Tests, Validation (skipped files), Home (reference to test status)

**DESCRIPTION:** App automatically generates pytest suites for your code and runs them. Three layers: health tests (snapshot), cached tests (previous runs), and dynamic tests (freshly generated).

**HOW IT WORKS:**

1. **Upload:** Files are uploaded to workspace.

2. **Automatic Proactive Generation:** If a file is 100% documented upon upload, the app begins generating tests in the background (non-blocking).

3. **Manual Run:** Click `▶️ Run Tests` in Dashboard / Tests to manually run the full suite.

4. **Execution Stages:**
   - Write workspace files to temp area.
   - Copy snapshot tests from Test/ folder (app health tests).
   - Generate AI tests for each fully-documented file.
   - Run pytest on both layers.
   - Collect results and display.

5. **Results:** Charts and detailed results show pass/fail counts, errors, and generated test code.

6. **Optimization:** Second run checks if workspace has changed. No changes = instant rerun with cached results. Changes = full regeneration.

**LAYERS:**

- **App Health Tests** (snapshot, 🛡️): Built-in tests validating the app itself. Located in Test/ folder.

- **Project Code Tests** (dynamic, 🛠️): AI-generated tests for your code. Generated fresh or cached from previous successful generations.

**EDGE CASES:**

- **Incomplete files:** Files with missing docstrings are skipped with a warning. Generate docstrings first in DocStrings tab.

- **Parse errors:** Files with syntax errors cannot be tested. Fix syntax errors first.

- **Slow generation:** First test run may take minutes if many files need test generation. Rerun is instant if nothing changed.

- **Test failures:** Failed tests show in red. Expand to see explanation and full traceback.

- **Skipped tests:** Some files may be skipped if generation fails. Clear cache and rerun to retry.

**TIPS:**

- Always run tests after major fixes to validate your changes.

- Failed tests may indicate bugs in your code or in the AI-generated tests. Review carefully.

- Use "Clear Cache" to force regeneration from scratch if results seem stale or inconsistent.


- Use "Clear Cache" to force regeneration from scratch if results seem stale or inconsistent.

- AI-generated tests are best-effort and may not cover all code paths. Manual review and additions recommended.

**FAQ:**

Q: How long does test generation take?
A: First run typically takes 30 seconds to several minutes depending on file count. Subsequent runs are instant if code hasn't changed. Clearing cache forces regeneration which takes time again.

Q: Why are some files skipped during test generation?
A: Files are skipped if they have incomplete documentation (not all functions have docstrings). Generate docstrings first using the DocStrings tab, then tests will be generated.

Q: Can I run tests for just one file instead of the whole workspace?
A: Not directly from the UI. Deselect files in the Sidebar to focus on specific files, then run tests. Tests will only generate for the selected files.

Q: What does "Health Tests" mean?
A: Health Tests are built-in tests for the AI Code Reviewer app itself (in the Test/ folder). They validate that the app is working correctly. Project tests are for your code.

Q: If a test fails, what should I do?
A: Expand the failed test to see the error message and traceback. This may indicate a bug in your code or the generated test may be incorrect. Review and either fix your code or manually edit the test.

Q: Can I edit generated tests?
A: The app doesn't have a built-in test editor. Copy the test code, edit it locally, then paste back or commit to your repo directly.

Q: Do tests auto-run in the background?
A: Tests don't automatically run after you fix code. You must click "Run Tests" to generate and execute the test suite. However, generation happens automatically for fully documented files upon upload.

Q: What if I want fresh tests and the cached ones seem outdated?
A: Click"Clear Cache" in the Tests tab. This deletes cached tests, forcing a fresh generation from scratch on your next "Run Tests".

[/CROSS_FEATURE]

---

## [CROSS_FEATURE: workspace-metrics-and-reporting]

**NAME:** Workspace Metrics and Reporting

**APPEARS IN:** Home, Dashboard / Advanced Filters, Dashboard / Export, Metrics Screen, File Tabs

**DESCRIPTION:** Real-time metrics tracking docstring coverage, validation status, and code quality across your workspace. Metrics update instantly as you fix code.

**METRICS PROVIDED:**

- **Total Files:** Count of uploaded files.

- **Files Having Doc String:** Count of files with at least one documented function.

- **Total Functions:** Sum of all functions across all files.

- **Functions Having Doc String:** Count of functions with docstrings.

- **Functions Not Having Doc String:** Count without docstrings.

- **Coverage Percentage:** Calculated as (Functions with docstrings / Total functions) × 100. Shown as percentage or "N/A".

- **Clean Files / Total Files:** Count of files with zero validation errors.

- **100% Compliant Functions:** Count of functions with zero docstring violations (PEP 257 + parameter docs).

- **Total Docstring Violations (PEP/Params):** Sum of all detected errors across all docstrings.

- **Detected Style:** Per-file docstring style (Google, reST, NumPy, Mixed, None/Incomplete).

**COLOR CODING:**

- **Green** (#7bed9f): 100% or excellent (all documented, zero errors, all clean).

- **Yellow** (#feca57): Partial or warning (some documented, < 100%, some errors).

- **Red** (#ff6b6b): Poor or critical (none documented, < 50%, many errors).

- **Gray** (#888): Not applicable (no functions, no data).

**REAL-TIME UPDATES:**

Metrics update instantly when you:
- Upload new files.
- Fix docstrings via AI.
- Convert or generate docstrings.
- Run validation.

No manual refresh needed.

**EXPORT OPTIONS:**

Metrics can be exported in 4 formats:
- JSON: For programmatic analysis.
- Markdown: For documentation and wikis.
- CSV: For spreadsheets and data tools.
- Plain Text: For simple human-readable reports.

**TIPS:**

- Monitor metrics on Home screen regularly to track progress toward 100% coverage.

- Use color coding to quickly identify weak areas (lots of red = high priority).



- Use color coding to quickly identify weak areas (lots of red = high priority).

- Export metrics after major milestones to create historical reports and track improvement over time.

- Check "Clean Files" and "Compliant Functions" metrics regularly to ensure quality during iteration.

**FAQ:**

Q: What does "Coverage Percentage" actually calculate?
A: It's (Functions with docstrings / Total functions) × 100. So if you have 50 functions and 40 have docstrings, coverage is 80%. This doesn't account for docstring quality, only existence.

Q: What's the difference between "Functions Having Doc String" and "100% Compliant Functions"?
A: Having a docstring means it exists. Compliant means it exists AND passes PEP 257 validation rules and all parameter documentation is complete. A function can have a docstring but not be compliant.

Q: How do metrics update in real-time?
A: When you fix docstrings, generate new ones, or run validation, metrics recalculate instantly based on the current workspace state. No refresh button needed.

Q: What do green, yellow, and red colors mean for each metric?
A: Green = excellent (100% or complete), Yellow = partial/warning (between 0-99% or some issues), Red = critical (0% or many issues). Gray means not applicable (no data).

Q: Can I compare metrics from two different time periods?
A: No built-in comparison. Export metrics (Download) at critical points, then manually compare reports to track progress over time.

Q: Does coverage percentage account for docstring quality?
A: No. It only counts if a docstring exists, not quality. Use the "Violations" metric to see quality issues. Use "100% Compliant" metric to see completely valid docstrings.

Q: Should I aim for 100% coverage?
A: Ideally yes, but sometimes small helper functions don't warrant docstrings. The app measures 100% to show clear goals, but your team should decide realistic targets.

Q: How is "Clean Files" different from coverage percentage?
A: Coverage is about documented functions (existence). Clean Files means files have zero validation/PEP 257 errors (quality). You can be 100% documented but not clean if docstrings have errors.

[/CROSS_FEATURE]

---

## [CROSS_FEATURE: file-management]

**NAME:** File Management (Upload, Add, Delete, Download)

**APPEARS IN:** Upload Screen, Sidebar, File Tabs, Dashboard

**DESCRIPTION:** Upload, add, delete, and download files throughout your workflow. Files persist in the workspace session until deleted.

**OPERATIONS:**

- **Initial Upload** (Upload Screen):
  - Drag .py or .zip files onto the file uploader.
  - Click `🚀 Analyze Workspace` to process.
  - App parses files and creates workspace directories.

- **Add Files** (Sidebar):
  - Click Add Files uploader in sidebar anytime.
  - Select additional .py or .zip files.
  - Files are processed immediately (no re-analyze button needed).
  - Workspace is updated with new files.

- **Delete File**:
  - Via sidebar: Click trash icon next to file name.
  - Via file tab: Click `Delete File` button in file header.
  - File is removed immediately from workspace and sidebar.
  - All caches and test results are cleared.
  - No undo—deletion is permanent.

- **Download File**:
  - Via sidebar: Click download icon next to file name.
  - Via file tab: Click `⬇️ Download` button.
  - File is downloaded as-is (original or AI-fixed version if applicable).
  - File name includes "fixed_" prefix if it was modified by AI.

- **Close File Tab** (without deleting):
  - Click `Close File` button in file header.
  - Tab is removed.
  - File remains in sidebar and workspace.
  - Useful for UI cleanup without losing data.

**SUPPORTED FORMATS:**

- **.py files:** Single Python source files. Parsed directly.

- **.zip archives:** Folders and files compressed into .zip format. App extracts all .py files and processes them with original folder structure preserved.

**EDGE CASES:**

- **Conflicting filenames:** If you upload a file with the same name as an existing file, it is replaced. Previous fixes are lost.

- **Large files:** Very large files may process slowly. No timeout limit enforced currently.

- **Broken zips:** If a .zip is corrupted, the upload fails with an error message. Only valid files are processed.

**TIPS:**

- Use .zip to upload entire project folders at once instead of selecting individual files.

- Download files frequently to keep local backups, especially after AI fixes.

- Use Close File to keep workspace tidy without losing files.


- Use Close File to keep workspace tidy without losing files.

- Delete files only when you're sure you don't need them anymore. Consider downloading first as a backup.

**FAQ:**

Q: What's the difference between Close File and Delete File?
A: Close File removes the tab visually but keeps the file in the sidebar. Delete File removes it completely from workspace and sidebar. Close for cleanup; Delete for permanent removal.

Q: Can I upload more files after the initial upload?
A: Yes. Use the Add Files uploader in the sidebar anytime. New files are processed immediately without needing to re-analyze the workspace.

Q: What file formats are supported?
A: Only .py (Python) and .zip (archives containing Python files). The app extracts .py files from .zip and preserves folder structure.

Q: If I upload a .zip file, are the folders preserved?
A: Yes. The app extracts all .py files from the .zip and maintains the original folder structure in the workspace sidebar.

Q: What happens if I upload a file with the same name as an existing file?
A: The new file replaces the old one. Any previous AI fixes or cached results for that file are lost. Download your previous version first as a backup if needed.

Q: Can I download a file without opening its tab?
A: Yes. Click the download icon in the sidebar next to the file name. This works for original files or AI-fixed versions.

Q: If a file was AI-fixed, does the download include the fixes?
A: Yes. Clicking download gets you the current version (AI-fixed if applicable). The downloaded file name includes "fixed_" prefix if it was modified.

Q: Is there an undo for deleted files?
A: No. Deletion is permanent. Re-upload the file from your backup or version control system if needed.

Q: Can I upload very large files?
A: Yes, but processing may be slow. No hard timeout limit currently. If it hangs, try uploading smaller .zip archives or individual files instead.

Q: What happens if I upload a broken or corrupted .zip file?
A: The upload fails with an error message. Only valid files are extracted and processed.

[/CROSS_FEATURE]

---

## [CROSS_FEATURE: ai-model-selection]

**NAME:** AI Model Selection and Override

**APPEARS IN:** Sidebar, Validation Tab (per-file), DocStrings Screen, Dashboard / Tests

**DESCRIPTION:** Choose which AI model (e.g., GPT-4, Claude) powers docstring fixing, generation, and conversion. Global default can be overridden per-file or per-operation.

**GLOBAL SELECTION:**

- Located in sidebar under "Choose AI Fix Model".
- Dropdown shows available models with user-friendly names (e.g., "GPT-4 Turbo", "Claude 3 Opus").
- Selected model is used by default for all AI operations.
- Can be changed anytime; new selections apply to all subsequent operations.

**PER-FILE OVERRIDE:**

- In Validation tab, when fixing a file, a dropdown appears: "Choose an AI Model to fix this file".
- This overrides the global choice just for that fix operation.
- Useful for trying different models on tricky files.

**PER-OPERATION MODEL SELECTION:**

- In DocStrings screen, when converting/generating, a Model dropdown appears.
- In Dashboard / Tests, no per-operation model override is shown (uses global default).

**MODEL DIFFERENCES:**

Different models may produce:
- Different docstring quality.
- Different handling of ambiguous signatures.
- Different performance (speed/cost).
- Different style adherence.

No one model is optimal for all cases. Experimentation recommended.

**TIPS:**

- Start with your preferred model in the sidebar (set once, use everywhere by default).

- If results are unsatisfactory, try a different model using the per-file or per-operation override.

- Some models may specialize in code understanding, others in style adherence. Trial and error helps find the best fit.

**KNOWN ISSUES:**


**KNOWN ISSUES:**

- Model availability depends on app configuration and API keys. Not all models may be available in all environments.

**FAQ:**

Q: Where do I select the AI model?
A: Click the "Choose AI Fix Model" dropdown in the sidebar. This is your global selection used for all AI operations by default.

Q: Can I use a different model for just one file?
A: Yes. In the Validation tab, when fixing a file, there's a model dropdown. Select a different model just for that file; it overrides your global choice.

Q: What models are available?
A: Common options include GPT-4, GPT-4 Turbo, Claude 3 Opus, Claude 3 Sonnet, and others. Availability depends on your API configuration. Check the dropdown in the sidebar to see your options.

Q: Why would I want to try different models?
A: Different models produce different docstring quality. Some excel at code understanding, others at style adherence. If one model produces poor results, try another.

Q: Does changing the model affect already-fixed files?
A: No. Model changes only affect new operations. Previously generated docstrings are not re-run when you change models.

Q: Which model should I start with?
A: Your app likely has a recommended default. Start with that, generate/fix some docstrings, then experiment with others if results aren't satisfactory.

Q: Does the model choice affect speed?
A: Yes. Faster/cheaper models may process quicker but with lower quality. Slower models may have higher quality but take longer. There's usually a tradeoff.

Q: Can I set a per-file default model permanently?
A: Not per-file permanently. You must select the model each time you fix that file. The global model (sidebar) is your only "set once" option.

[/CROSS_FEATURE]

---

## GENERAL TIPS & PATTERNS

### How to Fix Docstrings

1. **Check Home screen** for coverage percentage. Identify files with low coverage.

2. **Open Validation screen**. See which files have errors.

3. **In Validation, click `Fix {filename} with AI`** (single file) or `Fix All with AI` (multiple).

4. **Review the AI-generated docstrings** in the file tab. Check that they're accurate.

5. **If fixes look good, continue**. If not, download the file and review manually, or try a different AI model.

### How to Convert Docstring Styles

1. **Open DocStrings screen**.

2. **Select your file**. Note the detected style.

3. **Choose target style** (if docstrings exist, you'll see Conversion mode; if not, Generation mode).

4. **Choose scope**: Whole file or single function.

5. **Click Convert or Generate**. Wait for AI to process.

6. **Review the preview** (left = current, right = result).

7. **Check the diff** to understand changes.

8. **Click Apply** if satisfied. Click Dismiss if not.

### How to Validate and Fix Errors

1. **Open Validation screen**. Charts show error distribution.

2. **Click a file expander** to see specific errors.

3. **For each error, review the code** at the line number shown.

4. **Click `Fix {filename} with AI`** to have AI rewrite docstrings to fix violations.

5. **After fix, click Rerun Tests** in Dashboard / Tests to verify the fix worked.

### How to Run Tests

1. **Open Dashboard screen**.

2. **Click `🧪 Tests` sub-tab** (if not already there).

3. **Click `▶️ Run Tests`**. Wait for execution.

4. **Review the chart** showing pass/fail counts per test suite.

5. **Expand failing test suites** to see detailed error messages.

6. **Use error info to debug your code** (if Project Code tests fail) or report bugs (if App Health tests fail).

7. **Make fixes and click `▶️ Rerun Tests`**. Rerun is instant if workspace hasn't changed.

### How to Export Reports

1. **Choose your screen:**
   - **Dashboard / Export:** Workspace-wide report.
   - **Metrics Screen:** Workspace-wide report (similar).
   - **Individual File Tab:** File-specific report.

2. **Select export format:**
   - JSON: Programmatic use, data analysis.
   - Markdown: Documentation, GitHub wikis.
   - CSV: Spreadsheets, data tools.
   - Plain Text: Simple human-readable.

3. **Review the Live Preview** to ensure accuracy.

4. **Click Download** to save the report.

5. **Use the report** for sharing with team, historical tracking, or integration.

---

## KEYBOARD & MOUSE SHORTCUTS

- **File selection:** Click any file name in sidebar to open its tab.

- **Tab bar:** Scroll horizontally in the tab bar if many files are open.

- **Dropdowns:** Click to open, select option, or clear selection.

- **Buttons:** Click to trigger action.

- **Copy to clipboard:** Click Copy button in code sections; toast confirms.

- **Search Enter:** Press Enter in search box to apply search.

---

## TROUBLESHOOTING

### "No valid Python files found"

**Cause:** Uploaded files are not .py or extractable .zip files, or .zip contains no .py files.

**Solution:** Ensure files are Python (.py) or valid zip archives containing .py files.

---

### "Parse Error" in Home or Validation

**Cause:** File has syntax errors or couldn't be parsed by the app.

**Solution:** Check the file for syntax errors (mismatched brackets, indentation, etc.). Fix and re-upload.

---

### "Missing docstrings" in Tests

**Cause:** File has functions without docstrings. AI tests cannot be generated without docstring context.

**Solution:** Go to DocStrings screen, select the file, and click Generate to add docstrings. Then rerun tests.

---

### AI fixes don't look right

**Cause:** AI may have hallucinated docstring content or misunderstood the function.

**Solution:** Always review the diff before applying. If unsatisfactory, download the file, edit manually, and re-upload.

---

### Test failures

**Cause:** Your code has bugs, or AI-generated tests are incorrect.

**Solution:** Expand the failing test to see the error message. If it's a code bug, fix it. If the test is wrong, review the test code and disable/modify it.

---

### Model selection dropdown not showing

**Cause:** Global model default is selected. Per-file override appears only in specific contexts (Validation or DocStrings).

**Solution:** Use the sidebar to change the global default, or navigate to Validation / DocStrings where per-operation override is available.

---

## FREQUENTLY ASKED QUESTIONS

### Can I edit files directly in the app?

No. The app is read-only for viewing. Use the sidebar and file tabs to view code, but to edit, download the file, edit it locally, and re-upload. Alternatively, use AI fixes (Convert, Generate, Fix) which rewrite code without manual editing.

### Can I undo a file deletion?

No. File deletion is permanent. Consider downloading files before deleting them.

### Are my files stored on a server?

Only during your session. When you close the browser or app, files are cleared. No persistent storage. Workspace files are local to the session.

### How long does AI processing take?

Single operations (fix, convert, generate) typically take 5-30 seconds. Test generation take minutes for large workspaces. Rerun with no changes is instant.

### Can I use offline?

No. AI fixing, conversion, and generation require internet and API access to AI models. Static analysis (parsing, validation) is local.

### Do I have to use AI?

Not entirely. You can view, download, and manually edit files. You can run validation without fixes. Tests require docstrings but not AI fixes. But docstring generation and conversion require AI.

### What if I have a very large codebase?

Large files and many files slow things down, but there's no hard limit. Recommend splitting very large repos into chunks for faster processing.

### Can I share reports with my team?

Yes. Export reports in Markdown or CSV format and share the files. JSON exports can be integrated into CI/CD or data dashboards.

### What docstring styles are supported?

Three: Google, reST, and NumPy. The app detects style, validates against it, and can convert between styles.

### Can I customize validation rules?

Not directly in the UI. Validation is based on PEP 257 and parameter documentation standards. Custom rules would require code modification.

---

## END OF KNOWLEDGE BASE

---

**Document Version:** 1.0

**Last Updated:** 2026-03-18

**For AI Agent Use:** This document provides comprehensive screen-by-screen and feature-by-feature coverage of the AI Code Reviewer application. Use it to answer questions about functionality, UI elements, user actions, and expected states. When a user asks "What does this button do?" or "How do I fix my docstrings?", refer to the relevant [SCREEN] or [CROSS_FEATURE] section to extract accurate answers.
