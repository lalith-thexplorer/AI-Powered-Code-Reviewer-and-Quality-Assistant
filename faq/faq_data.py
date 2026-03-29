"""FAQ dataset for screen-specific help popup."""
import json

FAQ_DATA = json.loads(r'''{
    "upload-screen":  {
                          "screen_name":  "Upload Screen",
                          "faqs":  [
                                       {
                                           "q":  "Why is Analyze Workspace disabled?",
                                           "a":  "Analyze Workspace is enabled only after at least one valid .py or .zip file is selected in the uploader."
                                       },
                                       {
                                           "q":  "What file types are supported on the upload screen?",
                                           "a":  "Only .py and .zip files are accepted. Other file types are ignored by the uploader."
                                       },
                                       {
                                           "q":  "Can I upload multiple files at the same time?",
                                           "a":  "Yes. Multi-file upload is supported, and mixed selection of .py and .zip files is allowed."
                                       },
                                       {
                                           "q":  "How long does initial workspace analysis usually take?",
                                           "a":  "Typical analysis time is around 5 to 30 seconds depending on number of files, file sizes, and parse complexity."
                                       },
                                       {
                                           "q":  "What happens when I upload a zip file?",
                                           "a":  "The app extracts Python files from the archive and adds them to the workspace for parsing and analysis."
                                       },
                                       {
                                           "q":  "Why do I see errors right after upload?",
                                           "a":  "Parse errors usually mean one or more files contain invalid Python syntax. Fix the file and upload again."
                                       },
                                       {
                                           "q":  "Do files persist if I close the app?",
                                           "a":  "No. Workspace files are session-scoped and are cleared when the app session ends."
                                       },
                                       {
                                           "q":  "Can I return to upload mode after entering IDE mode?",
                                           "a":  "Yes. Remove all files from the workspace and the app will return to the upload state."
                                       },
                                       {
                                           "q":  "Can I use the app without internet on the upload step?",
                                           "a":  "Yes for upload and parsing. Internet is only required for AI-powered actions in later screens."
                                       },
                                       {
                                           "q":  "What should I do if upload appears stuck?",
                                           "a":  "Wait a few seconds for parsing to complete, then retry with smaller batches if needed. Also verify the selected files are valid Python sources."
                                       },
                                       {
                                           "q":  "Can I upload very large projects in one go?",
                                           "a":  "You can, but large uploads may take longer to parse. If performance drops, upload in smaller batches."
                                       },
                                       {
                                           "q":  "Will non-Python files inside a zip break upload?",
                                           "a":  "No. Non-Python files are skipped. Only Python files are parsed and added to workspace analysis."
                                       },
                                       {
                                           "q":  "Does upload automatically run validation and docstring fixes?",
                                           "a":  "No. Upload only parses files and prepares workspace data. Validation and AI actions are performed in their respective screens."
                                       },
                                       {
                                           "q":  "Can I replace an uploaded file with a new version?",
                                           "a":  "Yes. Re-upload the updated file and the workspace will use the new parsed content."
                                       },
                                       {
                                           "q":  "What happens if a file has encoding issues?",
                                           "a":  "The parser may fail to decode malformed files. Save files as UTF-8 where possible and upload again."
                                       },
                                       {
                                           "q":  "Is my uploaded code sent anywhere during upload?",
                                           "a":  "Upload and parsing happen locally in the app session. Code is sent to external AI providers only when you invoke AI features later."
                                       }
                                   ]
                      },
    "home-screen":  {
                        "screen_name":  "Home Screen",
                        "faqs":  [
                                     {
                                         "q":  "What do the colored metric cards mean?",
                                         "a":  "Green means excellent (100% or all documented), yellow means partial or warning (some issues), and red means poor or critical (mostly undocumented or many errors). Gray means the metric is not applicable."
                                     },
                                     {
                                         "q":  "Why do some files show a \"Mixed Styles Detected\" warning?",
                                         "a":  "Your file contains multiple different docstring formats (e.g., some Google-style and some reST-style mixed together). Use the DocStrings tab to convert all docstrings to a single consistent style."
                                     },
                                     {
                                         "q":  "How is Coverage Percentage calculated?",
                                         "a":  "It\u0027s the number of functions with docstrings divided by the total number of functions, multiplied by 100. A file with 8 documented functions out of 10 total functions would show 80% coverage."
                                     },
                                     {
                                         "q":  "Can I expand multiple file expanders at the same time?",
                                         "a":  "Yes. You can click to expand any number of file expanders, and they will all remain open simultaneously. Click again to collapse any individual file."
                                     },
                                     {
                                         "q":  "What should I do if a file shows \"Parse Error\"?",
                                         "a":  "The file likely has Python syntax errors that prevented the parser from reading it. Check the file for issues like mismatched brackets, indentation problems, or invalid syntax, then re-upload the corrected file."
                                     },
                                     {
                                         "q":  "If a file has zero functions, what coverage does it show?",
                                         "a":  "Files with no functions show \"N/A\" for coverage percentage, since there\u0027s nothing to document. This typically indicates the file contains only imports, constants, or class definitions without any function definitions."
                                     },
                                     {
                                         "q":  "Why would Coverage Percentage show as N/A but I have files uploaded?",
                                         "a":  "This means your workspace has zero functions across all files. Check your uploaded files to ensure they contain function definitions."
                                     },
                                     {
                                         "q":  "Can I delete a file from the Home screen?",
                                         "a":  "No, deletion is not available from Home. Go to the sidebar on the left, find the file, and click the trash icon to delete it."
                                     },
                                     {
                                         "q":  "What\u0027s the difference between \"Files Having Doc String\" and \"Functions Having Doc String\"?",
                                         "a":  "\"Files Having Doc String\" counts how many of your uploaded files contain at least one documented function. \"Functions Having Doc String\" counts the exact number of individual functions that are documented, which can be much larger if you have many functions per file."
                                     },
                                     {
                                         "q":  "How often do the metric cards update?",
                                         "a":  "Metrics update instantly whenever you make a change (upload new files, apply AI fixes, convert docstrings, or run validation). No manual refresh or button click required."
                                     }
                                 ]
                    },
    "dashboard-screen":  {
                             "screen_name":  "Dashboard Screen",
                             "faqs":  [
                                          {
                                              "q":  "What is the Dashboard for?",
                                              "a":  "Dashboard is your central workspace control panel. Use its sub-tabs to filter functions, search quickly, generate tests, export reports, and read in-app help."
                                          },
                                          {
                                              "q":  "Why does Dashboard content change when I switch sub-tabs?",
                                              "a":  "Each sub-tab focuses on a different workflow. Advanced Filters, Search, Tests, Export, and Help all share the same workspace data but present it differently."
                                          },
                                          {
                                              "q":  "Do Dashboard changes affect other screens?",
                                              "a":  "Yes. Actions like generating tests, fixing docstrings, or deleting files update shared workspace state, so Home, Validation, DocStrings, and Metrics will reflect those updates."
                                          },
                                          {
                                              "q":  "Why does Dashboard show no rows sometimes?",
                                              "a":  "This usually means current filters/search terms return zero matches, or there are no parsed functions in the selected files. Clear filters or recheck uploaded files."
                                          },
                                          {
                                              "q":  "How do I get back to a full workspace view?",
                                              "a":  "Reset filter/search controls in Dashboard and ensure all intended files are still present in the sidebar."
                                          }
                                      ]
                         },
    "dashboard-advanced-filters":  {
                                       "screen_name":  "Dashboard / Advanced Filters Sub-Tab",
                                       "faqs":  [
                                                    {
                                                        "q":  "How do I apply multiple filters at once?",
                                                        "a":  "Each filter selector is independent. Select your values for Doc string, File, Check result, and Sort by in any order. The table updates instantly to reflect all active filters combined."
                                                    },
                                                    {
                                                        "q":  "What does \"Workspace Shown\" mean in the metrics?",
                                                        "a":  "It\u0027s the percentage of your total functions that are currently visible after applying filters. If you have 100 functions total and 50 are showing, \"Workspace Shown\" would be 50%."
                                                    },
                                                    {
                                                        "q":  "Can I reset all filters to show everything again?",
                                                        "a":  "Yes. Set Doc string to \"All\", File to \"All files\", and Check result to \"Any\". The table immediately shows all functions again."
                                                    },
                                                    {
                                                        "q":  "What\u0027s the difference between sorting by \"Function name (A-Z)\" and \"Line number (Low-High)\"?",
                                                        "a":  "\"Function name (A-Z)\" sorts alphabetically regardless of which file the function is in. \"Line number (Low-High)\" sorts by file first, then by the line where the function appears within that file."
                                                    },
                                                    {
                                                        "q":  "How do I find all functions with validation errors?",
                                                        "a":  "Set Check result to \"Has issues\" in the filters. The table then shows only functions that have broken validation rules."
                                                    },
                                                    {
                                                        "q":  "Can I export only the filtered results?",
                                                        "a":  "Yes. The \"Download Filtered Results\" button exports only the rows currently visible after your filters are applied, not the entire workspace."
                                                    },
                                                    {
                                                        "q":  "Why would I filter by \"Check result\" = \"Not checked\"?",
                                                        "a":  "Functions show \"Not checked\" if they have no docstring at all. Filtering for this helps you find functions that are completely undocumented and need docstrings generated."
                                                    },
                                                    {
                                                        "q":  "If I change a filter, do my previous filter settings get saved?",
                                                        "a":  "No. Filter settings are only maintained during your current session. If you refresh the page or close the app, filters reset to defaults."
                                                    },
                                                    {
                                                        "q":  "Can I sort by multiple columns?",
                                                        "a":  "No. The \"Sort by\" dropdown allows only one sort order at a time. Choose the primary sort that matters most to you."
                                                    },
                                                    {
                                                        "q":  "What if my filtered result shows zero functions?",
                                                        "a":  "This means no functions in your workspace match the selected filter combination. Try broadening your filters (e.g., \"All\" instead of a specific file) to see if any functions match."
                                                    }
                                                ]
                                   },
    "dashboard-search":  {
                             "screen_name":  "Dashboard / Search Sub-Tab",
                             "faqs":  [
                                          {
                                              "q":  "How do I clear my search and see all functions again?",
                                              "a":  "Clear the text in the search box (leave it empty) and press Enter. The table immediately shows all functions again."
                                          },
                                          {
                                              "q":  "Is search case-sensitive?",
                                              "a":  "No. Search is case-insensitive, so searching \"Calculate\", \"calculate\", or \"CALCULATE\" returns the same results."
                                          },
                                          {
                                              "q":  "Can I search for partial words?",
                                              "a":  "Yes. Searching \"calc\" will find all functions with \"calc\" anywhere in the name (like \"calculate_total\", \"calculate_average\", \"recalculate\"). Searching matches anywhere in the function name or file name."
                                          },
                                          {
                                              "q":  "What\u0027s the difference between Search and Advanced Filters?",
                                              "a":  "Search is for finding specific functions by name or file path. Advanced Filters are for categorizing functions by documentation status (has/no docstring, validation issues). Use Search for \"find me this function\" and Filters for \"show me all functions like this\"."
                                          },
                                          {
                                              "q":  "Can I search in docstring content?",
                                              "a":  "No. Search only looks at function names and file paths, not the content of docstrings. To find content-specific issues, use the Validation tab."
                                          },
                                          {
                                              "q":  "Why do I need to press Enter for the search to apply?",
                                              "a":  "Pressing Enter prevents the app from updating the results with every keystroke you make. Type your full search term, then press Enter once to apply it. This makes the search faster and less resource-intensive."
                                          },
                                          {
                                              "q":  "Can I use wildcards or regex in search?",
                                              "a":  "No. Search is literal text matching only. Wildcards and regex patterns are not supported."
                                          },
                                          {
                                              "q":  "If I search for \"test\", will it find a function called \"test_module\"?",
                                              "a":  "Yes. Search matches \"test\" anywhere in the function name or file path, so \"test_module\", \"my_test\", \"retest\", and similar would all be found."
                                          },
                                          {
                                              "q":  "Can I download search results like I can with filters?",
                                              "a":  "Search results display in a table but don\u0027t have a dedicated download button. Use Dashboard \u003e Export to generate a full report, or use Advanced Filters \u003e Download Filtered Results for an equivalent download option."
                                          },
                                          {
                                              "q":  "What if I search for something with zero matches?",
                                              "a":  "The page shows an info message \"No functions match the criteria.\" and the table remains empty. Try a broader search term."
                                          }
                                      ]
                         },
    "dashboard-tests":  {
                            "screen_name":  "Dashboard / Tests Sub-Tab",
                            "faqs":  [
                                         {
                                             "q":  "Why does it say a test is \"skipped\"?",
                                             "a":  "Skipped means the AI generator could not create a meaningful test for that function. Typical reasons include simple passthrough logic, temporary API issues, or unsupported code patterns."
                                         },
                                         {
                                             "q":  "What is the difference between health snapshot tests and project tests?",
                                             "a":  "Health snapshot tests are a baseline generated once for comparison over time. Project tests are the active suite generated for your current workspace iteration."
                                         },
                                         {
                                             "q":  "Why is the first test generation run slow?",
                                             "a":  "The first run requires full function analysis and AI generation per target. Later runs are faster when cached outputs are reused."
                                         },
                                         {
                                             "q":  "What does Clear Cache do in Tests?",
                                             "a":  "It removes cached generated tests so the next run regenerates them from scratch. Use it after major code changes or if cached results seem stale."
                                         },
                                         {
                                             "q":  "Can I inspect generated test code?",
                                             "a":  "Yes. Open the relevant file tab or generated test artifact to review content before using it in CI."
                                         },
                                         {
                                             "q":  "Why did generation fail for some functions?",
                                             "a":  "Common causes are API rate limits, transient network failures, or code patterns the model could not safely test. Retry after a short delay or switch model."
                                         },
                                         {
                                             "q":  "Do tests regenerate every time I open the Tests tab?",
                                             "a":  "No. Existing cache is reused unless you explicitly regenerate or clear cache."
                                         },
                                         {
                                             "q":  "Can I generate tests for selected files only?",
                                             "a":  "Yes. Keep only target files in the workspace selection scope, then run generation."
                                         },
                                         {
                                             "q":  "Why should I review generated tests manually?",
                                             "a":  "AI tests can miss edge cases or make assumptions. Review before merging to ensure they match real behavior and project conventions."
                                         },
                                         {
                                             "q":  "Why do I see zero tests in the table?",
                                             "a":  "Either tests have not been generated yet, filters hide all rows, or all candidates were skipped. Regenerate and verify filters."
                                         }
                                     ]
                        },
    "dashboard-export":  {
                             "screen_name":  "Dashboard / Export Sub-Tab",
                             "faqs":  [
                                          {
                                              "q":  "What format should I choose for exporting?",
                                              "a":  "JSON is best for programmatic analysis or as an archive. Markdown is ideal for human-readable documentation and team wikis. CSV works with Excel and other spreadsheet tools. Plain Text is simplest but less structured."
                                          },
                                          {
                                              "q":  "Can I edit the report after exporting?",
                                              "a":  "Yes, all exported files are standard formats. Edit Markdown in any text editor, JSON in code editors, CSV in Excel, and Plain Text anywhere. Changes won\u0027t affect your workspace analysis until you re-export."
                                          },
                                          {
                                              "q":  "How is Export different from the Metrics screen?",
                                              "a":  "Export creates snapshot reports at this moment. Metrics shows live statistics of your current workspace. Export is for sharing/archiving; Metrics is for monitoring trends and real-time status."
                                          },
                                          {
                                              "q":  "Does the export auto-update if I change my code?",
                                              "a":  "No. Exports are static snapshots at the time you click Download. If you change code or upload new files, run Export again to get an updated report."
                                          },
                                          {
                                              "q":  "Can I export only certain functions or files?",
                                              "a":  "No directly. Use Advanced Filters first to narrow your view, then the export will include all currently visible functions. This gives you flexible subset exporting based on your filter criteria."
                                          },
                                          {
                                              "q":  "What information is included in each export?",
                                              "a":  "All exports include function names, file paths, docstring status, validation results, docstring style (if applicable), and any error messages. Markdown includes formatting and structure. JSON includes all metadata. CSV includes all columns that fit the format."
                                          },
                                          {
                                              "q":  "Can I share exported reports with team members who don\u0027t have access to this app?",
                                              "a":  "Yes. Exported files are standard formats readable by any text editor or spreadsheet tool. Send the file directly; no app access needed to view it."
                                          },
                                          {
                                              "q":  "What\u0027s the maximum file size for an export?",
                                              "a":  "Exports are limited by your browser\u0027s download speed and system memory. Large workspaces (1000+ functions) may take 30+ seconds to generate. If export fails, reduce workspace size or generate smaller reports with filtered views."
                                          }
                                      ]
                         },
    "dashboard-help":  {
                           "screen_name":  "Dashboard / Help Sub-Tab",
                           "faqs":  [
                                        {
                                            "q":  "Where do I find help if I\u0027m stuck?",
                                            "a":  "Click the \"Dashboard \u003e Help\" tab. The entire tab is searchable documentation. For quick answers, search the Help tab directly. For more complex issues, check Troubleshooting section in this Knowledge Base."
                                        },
                                        {
                                            "q":  "Can I search within the Help tab?",
                                            "a":  "Yes. There\u0027s a search box at the top of the Help tab. Type your question or keyword and matching help articles appear instantly."
                                        },
                                        {
                                            "q":  "What if I can\u0027t find the answer to my question?",
                                            "a":  "The Help tab covers all major features. If your issue isn\u0027t documented, it might be a bug or edge case not yet covered. Report the issue through GitHub or contact support."
                                        },
                                        {
                                            "q":  "Can I print the help documentation?",
                                            "a":  "Yes. Click the print icon in the Help tab header or use your browser\u0027s Print function (Ctrl+P / Cmd+P). The help content will print in readable format."
                                        },
                                        {
                                            "q":  "Can I keep the Help tab visible while working on other tabs?",
                                            "a":  "The Help tab works like any other tab. You can keep it open and switch between tabs to reference help while working. Help context doesn\u0027t disappear when you switch tabs."
                                        },
                                        {
                                            "q":  "Does this app update the help docs automatically?",
                                            "a":  "Help documentation is bundled with the app. When you update the app, help is updated automatically. Check the main app README for what\u0027s new in each version."
                                        },
                                        {
                                            "q":  "Who maintains this Help documentation?",
                                            "a":  "The help section is maintained by the core app developers and updated with each release. Feedback helps improve the documentation. Report typos, unclear explanations, or missing topics through GitHub."
                                        },
                                        {
                                            "q":  "Can I access Help if I\u0027m offline?",
                                            "a":  "Yes. Help documentation is built-in. You don\u0027t need internet to access it. The entire Help tab works offline."
                                        }
                                    ]
                       },
    "validation-screen":  {
                              "screen_name":  "Validation Screen",
                              "faqs":  [
                                           {
                                               "q":  "Why does it say my files are skipped?",
                                               "a":  "Files are skipped if they have incomplete docstrings (not all functions are documented). Validation only works on fully documented files. Go to DocStrings tab to generate missing docstrings first."
                                           },
                                           {
                                               "q":  "What do the error codes like D100 and D401 mean?",
                                               "a":  "These are PEP 257 docstring style codes that indicate violations. D200 = missing summary line, D401 = must use imperative mood, DAR101 = missing parameter documentation. Visit the Error Codes section below for details on each code the app can identify."
                                           },
                                           {
                                               "q":  "How long does it take to fix a file with AI?",
                                               "a":  "Typically 5-20 seconds per file, depending on file size and AI model speed. Large files may take longer. You can monitor progress with the AI is fixing spinner."
                                           },
                                           {
                                               "q":  "Can I fix individual rules or do I have to fix the whole file?",
                                               "a":  "You must fix the whole file at once through the UI. The AI reads all errors and fixes them together. If you want finer control, download the file, edit manually, and re-upload."
                                           },
                                           {
                                               "q":  "Can I override the AI model for a single file?",
                                               "a":  "Yes. Each file has its own model dropdown. Select a different model before clicking Fix and that model will be used just for that file."
                                           },
                                           {
                                               "q":  "Can I undo a fix if the AI gets something wrong?",
                                               "a":  "No direct undo in the app, but the original file is preserved. Re-upload the original if needed. Always review AI changes before committing to your codebase."
                                           },
                                           {
                                               "q":  "Why do some files show error charts and others don\u0027t?",
                                               "a":  "Error charts only appear when all files are fully documented. If some files are incomplete (missing docstrings), validation charts are hidden until you generate those missing docstrings."
                                           },
                                           {
                                               "q":  "Can I validate only certain files or must I validate everything?",
                                               "a":  "Validation runs on all uploaded files. To focus on specific files, deselect others in the Sidebar, then validation and fixing will only apply to the selected files."
                                           },
                                           {
                                               "q":  "What should I do after the AI fixes validation errors?",
                                               "a":  "Review the changes carefully-check the diff pills to see what was modified. Read the fixed docstrings to ensure they match your actual function logic. Then commit the changes to your repository."
                                           },
                                           {
                                               "q":  "Why did the AI fix fail for my function?",
                                               "a":  "Common causes: API quota exceeded, network interrupted, or the function code is too complex for the AI. Wait a few minutes and retry, or try a different AI model."
                                           },
                                           {
                                               "q":  "What does error code D200 mean?",
                                               "a":  "D200: Docstring has no summary line. Every docstring must start with a one-line summary. Fix: Add a concise summary sentence immediately after the opening triple-quotes, before any blank lines."
                                           },
                                           {
                                               "q":  "What does error code D400 mean?",
                                               "a":  "D400: First line must end with a period. The summary line must end with punctuation. Fix: Add a period at the end of the summary line. Example: Parse the input file. instead of Parse the input file"
                                           },
                                           {
                                               "q":  "What does error code D401 mean?",
                                               "a":  "D401: First line must use imperative mood. Write the summary as a command: Hash the password. not Hashes the password. Fix: Use the base verb form. Ask Does this function X? and write X."
                                           },
                                           {
                                               "q":  "What does error code D403 mean?",
                                               "a":  "D403: First word must be capitalized. The first character must be uppercase. Fix: Capitalize the first letter. Example: Hash the password. not hash the password."
                                           },
                                           {
                                               "q":  "What does error code D404 mean?",
                                               "a":  "D404: First word must not be This. Avoid starting with This function... or This method... Instead, use imperative: Calculate the sum. not This function calculates the sum."
                                           },
                                           {
                                               "q":  "What does error code D415 mean?",
                                               "a":  "D415: First line must end with period, question mark, or exclamation mark. Fix: Ensure the summary ends with . ? or !. Example: Parse the config file. or Is this valid?"
                                           },
                                           {
                                               "q":  "What does error code D205 mean?",
                                               "a":  "D205: Need exactly one blank line between summary and description. If your docstring has a multi-line description, ensure exactly one blank line separates the summary from the rest."
                                           },
                                           {
                                               "q":  "What does error code D212 mean?",
                                               "a":  "D212: Summary must be on the first line after the opening triple-quotes with no blank line before it. Fix: Remove any blank lines between the opening triple-quotes and the summary text."
                                           },
                                           {
                                               "q":  "What does error code D300 mean?",
                                               "a":  "D300: Use triple double-quotes, not triple single-quotes. Docstrings must use triple double-quotes (the standard). Fix: Replace all triple single-quotes with triple double-quotes at docstring start and end."
                                           },
                                           {
                                               "q":  "What does error code DAR101 mean?",
                                               "a":  "DAR101: A function parameter is missing from the Args section. The function has parameters but the docstring doesn\u0027t document them. Fix: Add or complete the Args section listing all parameters with type and description."
                                           },
                                           {
                                               "q":  "What does error code DAR201 mean?",
                                               "a":  "DAR201: Function returns a value but the Returns section is missing. The function has return statements but the docstring doesn\u0027t document the return. Fix: Add a Returns section with type and description of what is returned."
                                           },
                                           {
                                               "q":  "What does error code DAR301 mean?",
                                               "a":  "DAR301: Function raises exceptions but the Raises section is missing. The function has raise statements but doesn\u0027t document them. Fix: Add a Raises section listing exceptions that can be raised and when."
                                           },
                                           {
                                               "q":  "What does error code D412 mean?",
                                               "a":  "D412: No blank lines allowed between section header and content. Section headers like Args: must be followed immediately by content on the next line with no blank lines between."
                                           },
                                           {
                                               "q":  "What does error code D413 mean?",
                                               "a":  "D413: Missing blank line after last section. After the final section header and content, add a blank line before the closing triple-quotes to properly structure the docstring."
                                           },
                                           {
                                               "q":  "What is the difference between D4xx and DAR codes?",
                                               "a":  "D4xx codes (D400, D401, D403, etc.) are PEP 257 formatting rules enforced by pydocstyle. DAR codes (DAR101, DAR201, DAR301) are enforced by Darglint and check that parameters, returns, and exceptions are documented."
                                           },
                                           {
                                               "q":  "Which error codes can the app automatically fix?",
                                               "a":  "The AI can fix most codes: D200 (missing summary), D400/D401/D403/D404/D415 (summary format), D205/D212/D300 (structure), DAR101/DAR201/DAR301 (missing sections). Some rare codes may require manual fixes."
                                           },
                                           {
                                               "q":  "Are some error codes ignored by the validation system?",
                                               "a":  "Yes. To reduce noise, these cosmetic codes are ignored: D201 (blank line before), D202 (blank line after), D203 (class spacing), D213 (multi-line summary), D412/D413 (section spacing). The app focuses on critical issues instead."
                                           }
                                       ]
                          },
    "docstrings-screen":  {
                              "screen_name":  "DocStrings Screen",
                              "faqs":  [
                                           {
                                               "q":  "What\u0027s the difference between \"Generate\" and \"Convert\"?",
                                               "a":  "Generate creates brand-new docstrings from scratch for functions that have none. Convert takes existing docstrings and changes them from one style (Google) to another (NumPy, reST). Use Generate if no docstrings exist; use Convert to change the style."
                                           },
                                           {
                                               "q":  "Can I convert just one function in a file instead of the whole file?",
                                               "a":  "Yes. Use the Scope Selector dropdown. Select the specific function name and only that function will be converted. Other functions stay unchanged. This is useful for iterating on specific functions."
                                           },
                                           {
                                               "q":  "What does \"Mixed\" style mean?",
                                               "a":  "Mixed means your file contains docstrings in multiple styles (some Google, some reST, etc.). To clean this up, select \"Whole File\" and choose a target style to make all docstrings consistent."
                                           },
                                           {
                                               "q":  "How does the app detect the docstring style?",
                                               "a":  "The app analyzes the format of existing docstrings (structure, keywords, indentation) and matches them to the known patterns for Google, reST, and NumPy. Mixed means multiple patterns were found."
                                           },
                                           {
                                               "q":  "Can I preview the converted code before applying it?",
                                               "a":  "Yes. After clicking Convert, the preview shows the current code on the left and the target-style code on the right. Review both before choosing to Apply, Dismiss, Copy, or Download."
                                           },
                                           {
                                               "q":  "What happens when I click \"Apply\"?",
                                               "a":  "The converted docstrings replace the originals in your workspace. Your file is immediately updated. Tests are regenerated if the file is now fully documented. You cannot undo-review carefully before applying."
                                           },
                                           {
                                               "q":  "Should I review generated docstrings?",
                                               "a":  "Yes, always. AI sometimes makes assumptions or hallucinates details, especially for complex functions. Read the generated docstrings to ensure they match your actual function logic and parameters."
                                           },
                                           {
                                               "q":  "Can I edit a generated docstring before applying?",
                                               "a":  "Not directly in the preview. Copy the code, paste it into a text editor, make edits, then you can download the modified file. Apply is all-or-nothing-you apply the entire generated preview."
                                           },
                                           {
                                               "q":  "Can I revert a style conversion if I change my mind?",
                                               "a":  "No built-in undo. If you want to revert, re-upload the original file from your version control system, or use Convert again with the previous style selected (though this may not perfectly restore)."
                                           },
                                           {
                                               "q":  "Why does it show \"No changes detected\"?",
                                               "a":  "This means the AI determined your docstrings are already in the target style or don\u0027t need modification. The current and generated versions are identical. This is normal if you\u0027ve already converted or if the conversion makes no changes."
                                           }
                                       ]
                          },
    "metrics-screen":  {
                           "screen_name":  "Metrics Screen",
                           "faqs":  [
                                        {
                                            "q":  "Is the Metrics screen the same as Dashboard / Export?",
                                            "a":  "Similar but slightly different. Both give you workspace overview exports. Dashboard/Export is a snapshot tab. Metrics is the dedicated reporting screen. Use whichever feels natural for your workflow-both produce identical reports."
                                        },
                                        {
                                            "q":  "What information is included in the metrics report?",
                                            "a":  "All reports include: file names, function counts, documentation status for each function, validation errors, docstring styles detected, and file-by-file analysis. The exact format depends on your export choice (JSON, Markdown, CSV, or Plain Text)."
                                        },
                                        {
                                            "q":  "Can I schedule metrics to be generated at a certain time?",
                                            "a":  "No. Metrics are generated on-demand when you click Download. To track trends over time, you\u0027d need to manually download reports and compare them."
                                        },
                                        {
                                            "q":  "Can I compare metrics from two different time periods?",
                                            "a":  "No built-in comparison feature. Download reports from different dates, then compare them manually in Excel or a text editor to track changes in documentation coverage."
                                        },
                                        {
                                            "q":  "Do the metrics include validation errors from the Validation screen?",
                                            "a":  "Yes. If files have validation errors, those are included in the report. The exact level of detail depends on your format choice (JSON has most detail, Plain Text has less)."
                                        },
                                        {
                                            "q":  "Can I export just the metrics without function-level details?",
                                            "a":  "No. Exports include all details. To export a summary-only, download as Plain Text-it is the most concise option."
                                        },
                                        {
                                            "q":  "What tests are included in the metrics report?",
                                            "a":  "Test counts and status are included for reporting purposes. If a function has AI-generated tests, that status is reported. Actual test code isn\u0027t included in the metrics export, only TestStatus."
                                        },
                                        {
                                            "q":  "How often should I generate fresh metrics?",
                                            "a":  "Generate metrics whenever you\u0027ve made significant changes: after fixing docstrings, after running validation, or periodically for monitoring. Each download captures the current state of your workspace."
                                        },
                                        {
                                            "q":  "Can I see metrics for just one file?",
                                            "a":  "No. Metrics tab exports your entire workspace. For single-file metrics, open that file\u0027s tab (File Tab screen) where file-level stats are shown."
                                        },
                                        {
                                            "q":  "What\u0027s the file size of a typical metrics export?",
                                            "a":  "Depends on workspace size. 50 functions ~ 50KB. 500 functions ~ 500KB. If export is too large, try exporting CSV or Plain Text (smaller than JSON)."
                                        }
                                    ]
                       },
    "file-tab":  {
                     "screen_name":  "Individual File Tab (Opened From Sidebar)",
                     "faqs":  [
                                  {
                                      "q":  "What\u0027s the difference between \"Close File\" and \"Delete File\"?",
                                      "a":  "Close File removes the tab (you won\u0027t see it open) but keeps the file in the sidebar. Delete File removes the file completely from your workspace and sidebar. Use Close for temporary cleanup; use Delete to remove unwanted files permanently."
                                  },
                                  {
                                      "q":  "What does \"AI Fixed\" mean in the file tab title?",
                                      "a":  "If the file was processed by Validation \u003e Fix All or Fix {filename}, it shows \"AI Fixed\". This means the AI modified the docstrings. Check the diff pills (showing lines added/removed) to see what changed."
                                  },
                                  {
                                      "q":  "Can I see what the original code looked like before AI fixed it?",
                                      "a":  "Yes. The diff pills show summary statistics. For full details, re-upload the original file from your git repository or backup, then compare side-by-side in two tabs."
                                  },
                                  {
                                      "q":  "What do the diff pills show?",
                                      "a":  "Two pills appear: green pill shows \"+ N lines added/modified\" and red pill shows \"- N lines removed\". These indicate the scope of AI changes to the docstrings."
                                  },
                                  {
                                      "q":  "Can I verify the fix is correct before committing to my repo?",
                                      "a":  "Yes. Review the code in the Current Code section. Use Copy to paste into a temporary file and verify correctness. If satisfied, use Download and then commit to your repo."
                                  },
                                  {
                                      "q":  "Can I edit the code directly in the file tab?",
                                      "a":  "No. The file tab is read-only. If you need to edit manually, Download the code, edit it locally, then re-upload the modified version."
                                  },
                                  {
                                      "q":  "Can I export or download just the docstrings from this file?",
                                      "a":  "You can download the entire file from the Current Code section. For report-only output, use the Export Report section to generate file-specific JSON, Markdown, CSV, or Plain Text."
                                  },
                                  {
                                      "q":  "How is the per-file export different from workspace-level export?",
                                      "a":  "Per-file export shows only this file\u0027s functions and their status. Workspace export (from Metrics or Dashboard/Export) shows all files. Use per-file for focused reports to share with a colleague about one file."
                                  },
                                  {
                                      "q":  "Can I have multiple files open in tabs at the same time?",
                                      "a":  "Yes. Clicking multiple files from the sidebar opens them in different tabs. You can switch between tabs to compare files side-by-side or work on multiple files sequentially."
                                  },
                                  {
                                      "q":  "What happens to this tab if I delete the file?",
                                      "a":  "The tab closes immediately. The file is removed from the workspace and sidebar. If you need it back, re-upload the original from your backup or version control system."
                                  }
                              ]
                 },
    "sidebar":  {
                    "screen_name":  "Left Sidebar (Explorer Panel)",
                    "faqs":  [
                                 {
                                     "q":  "Can I collapse or hide the sidebar to get more screen space?",
                                     "a":  "No. The sidebar is fixed and always visible in this version. There\u0027s no collapse button to hide it. You get full use of it to navigate and select files."
                                 },
                                 {
                                     "q":  "How do I navigate to different screens in the app?",
                                     "a":  "Use the Navigation dropdown in the sidebar. It shows all 5 screens (Home, Dashboard, DocStrings, Validation, Metrics). Select one to switch to that screen instantly."
                                 },
                                 {
                                     "q":  "What happens if I change the AI Fix Model in the sidebar?",
                                     "a":  "This changes the global model selection for all AI operations (fixes, generations, conversions). All subsequent AI tasks use the new model. You can still override it per-file in the Validation tab for specific files."
                                 },
                                 {
                                     "q":  "Can each file use a different AI model?",
                                     "a":  "Not by default. The sidebar model is global. But in the Validation tab, you can select a different model just for that file before clicking \"Fix {filename}\". This is a per-file override."
                                 },
                                 {
                                     "q":  "What file formats can I add to my workspace?",
                                     "a":  "Only `.py` (Python) and `.zip` files. The uploader has a yellow dashed border. Zip files are automatically extracted; Python files are added directly."
                                 },
                                 {
                                     "q":  "Why is the file list showing very long names truncated?",
                                     "a":  "The sidebar has fixed width. Long file names are compressed. Hover your cursor over a truncated name to see the full path in a tooltip."
                                 },
                                 {
                                     "q":  "Can I reorder files in the file list?",
                                     "a":  "No. Files are listed in the order they were uploaded. To change order, delete unwanted files or re-upload in the desired order."
                                 },
                                 {
                                     "q":  "Can I download a file directly from the sidebar file list?",
                                     "a":  "Yes, there\u0027s a download icon (middle column) next to each file name. Click it to download the current (or AI-fixed) version without opening the file tab."
                                 },
                                 {
                                     "q":  "How do I delete a file from the workspace?",
                                     "a":  "Click the trash icon (right column) in the file list. There is no confirmation modal-the file is deleted immediately. To recover, re-upload from your backup or version control system."
                                 },
                                 {
                                     "q":  "Can I search the file list to find a specific file?",
                                     "a":  "No built-in search in the sidebar. If you have many files, scroll through the file list or hover/read tooltips to find the one you want."
                                 }
                             ]
                },
    "general":  {
                    "screen_name":  "General Help",
                    "faqs":  [
                                 {
                                     "q":  "Where do I find help if I\u0027m stuck?",
                                     "a":  "Click the \"Dashboard \u003e Help\" tab. The entire tab is searchable documentation. For quick answers, search the Help tab directly. For more complex issues, check Troubleshooting section in this Knowledge Base."
                                 },
                                 {
                                     "q":  "How do I navigate to different screens in the app?",
                                     "a":  "Use the Navigation dropdown in the sidebar. It shows all 5 screens (Home, Dashboard, DocStrings, Validation, Metrics). Select one to switch to that screen instantly."
                                 },
                                 {
                                     "q":  "What file formats can I add to my workspace?",
                                     "a":  "Only `.py` (Python) and `.zip` files. The uploader has a yellow dashed border. Zip files are automatically extracted; Python files are added directly."
                                 },
                                 {
                                     "q":  "What\u0027s the difference between \"Close File\" and \"Delete File\"?",
                                     "a":  "Close File removes the tab (you won\u0027t see it open) but keeps the file in the sidebar. Delete File removes the file completely from your workspace and sidebar. Use Close for temporary cleanup; use Delete to remove unwanted files permanently."
                                 },
                                 {
                                     "q":  "Where do I select the AI model?",
                                     "a":  "Click the \"Choose AI Fix Model\" dropdown in the sidebar. This is your global selection used for all AI operations by default."
                                 },
                                 {
                                     "q":  "Can I use a different model for just one file?",
                                     "a":  "Yes. In the Validation tab, when fixing a file, there\u0027s a model dropdown. Select a different model just for that file; it overrides your global choice."
                                 },
                                 {
                                     "q":  "How is Export different from the Metrics screen?",
                                     "a":  "Export creates snapshot reports at this moment. Metrics shows live statistics of your current workspace. Export is for sharing/archiving; Metrics is for monitoring trends and real-time status."
                                 },
                                 {
                                     "q":  "Why does it say my files are skipped?",
                                     "a":  "Files are skipped if they have incomplete docstrings (not all functions are documented). Validation only works on fully documented files. Go to DocStrings tab to generate missing docstrings first."
                                 }
                             ]
                }
}''')
