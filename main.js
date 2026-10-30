/**
 * Automated Syntax and Semantic Analysis System - Frontend Controller
 * Mini-project for Compiler Design Course
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const codeEditor = document.getElementById("codeEditor");
    const lineNumbers = document.getElementById("lineNumbers");
    const sampleSelector = document.getElementById("sampleSelector");
    const btnAnalyze = document.getElementById("btnAnalyze");
    const btnClear = document.getElementById("btnClear");
    const sampleTag = document.getElementById("sampleTag");

    // Summary Elements
    const statusLexical = document.getElementById("statusLexical");
    const statusSyntax = document.getElementById("statusSyntax");
    const statusSemantic = document.getElementById("statusSemantic");
    const finalVerdict = document.getElementById("finalVerdict");

    const indicatorLexical = document.getElementById("indicatorLexical");
    const indicatorSyntax = document.getElementById("indicatorSyntax");
    const indicatorSemantic = document.getElementById("indicatorSemantic");
    const indicatorStatus = document.getElementById("indicatorStatus");

    const tokensCount = document.getElementById("tokensCount");
    const astCount = document.getElementById("astCount");
    const symbolCount = document.getElementById("symbolCount");
    const errorCount = document.getElementById("errorCount");

    // Tabs
    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabPanels = document.querySelectorAll(".tab-panel");
    const errorsTabBadge = document.getElementById("errorsTabBadge");

    // Containers
    const verdictBanner = document.getElementById("verdictBanner");
    const errorsContainer = document.getElementById("errorsContainer");
    const tokensTable = document.getElementById("tokensTable").querySelector("tbody");
    const astContainer = document.getElementById("astContainer");
    const derivationLog = document.getElementById("derivationLog");
    const symbolTable = document.getElementById("symbolTable").querySelector("tbody");
    const symbolScopeCount = document.getElementById("symbolScopeCount");
    const filteredTokenCount = document.getElementById("filteredTokenCount");

    // Modal
    const grammarModal = document.getElementById("grammarModal");
    const btnGrammarModal = document.getElementById("btnGrammarModal");
    const btnModalClose = document.getElementById("btnModalClose");
    const btnModalOk = document.getElementById("btnModalOk");
    const grammarCodeDisplay = document.getElementById("grammarCodeDisplay");
    const btnExportJson = document.getElementById("btnExportJson");

    // State
    let samplesCache = {};
    let currentAnalysisData = null;
    let allTokens = [];
    let currentFilter = "all";

    // ---------------- Line Numbers & Editor ----------------

    function updateLineNumbers() {
        const lines = codeEditor.value.split("\n");
        const count = Math.max(lines.length, 1);
        let numHtml = "";
        for (let i = 1; i <= count; i++) {
            numHtml += i + "<br>";
        }
        lineNumbers.innerHTML = numHtml;
    }

    codeEditor.addEventListener("input", updateLineNumbers);
    codeEditor.addEventListener("scroll", () => {
        lineNumbers.scrollTop = codeEditor.scrollTop;
    });

    // Handle Tab key in editor
    codeEditor.addEventListener("keydown", (e) => {
        if (e.key === "Tab") {
            e.preventDefault();
            const start = codeEditor.selectionStart;
            const end = codeEditor.selectionEnd;
            codeEditor.value = codeEditor.value.substring(0, start) + "    " + codeEditor.value.substring(end);
            codeEditor.selectionStart = codeEditor.selectionEnd = start + 4;
            updateLineNumbers();
        }

        // Ctrl + Enter or Cmd + Enter to Analyze
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            e.preventDefault();
            runAnalysis();
        }
    });

    // ---------------- Tab Navigation ----------------

    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");
            tabButtons.forEach(b => b.classList.remove("active"));
            tabPanels.forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            document.getElementById(targetTab).classList.add("active");
        });
    });

    // ---------------- Samples API & Selector ----------------

    async function loadSamplesList() {
        try {
            const res = await fetch("/api/samples");
            const data = await res.json();
            if (data.status === "success") {
                samplesCache = {};
                data.samples.forEach(s => {
                    samplesCache[s.id] = s;
                });
            }
        } catch (err) {
            console.error("Failed to load samples:", err);
        }
    }

    function selectSample(sampleId) {
        if (!samplesCache[sampleId]) return;
        const sample = samplesCache[sampleId];
        codeEditor.value = sample.code;
        sampleSelector.value = sampleId;
        sampleTag.textContent = sample.title;
        sampleTag.className = sample.category.startsWith("Valid") ? "badge badge-success" : "badge badge-danger";
        updateLineNumbers();
        runAnalysis();
    }

    sampleSelector.addEventListener("change", (e) => {
        selectSample(e.target.value);
    });

    document.querySelectorAll(".pill-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const sampleId = btn.getAttribute("data-sample");
            selectSample(sampleId);
        });
    });

    btnClear.addEventListener("click", () => {
        codeEditor.value = "";
        sampleSelector.value = "";
        sampleTag.textContent = "Custom Code";
        sampleTag.className = "badge badge-neutral";
        updateLineNumbers();
        resetResults();
    });

    function resetResults() {
        statusLexical.textContent = "Ready";
        statusSyntax.textContent = "Ready";
        statusSemantic.textContent = "Ready";
        finalVerdict.textContent = "Awaiting Input";

        indicatorLexical.className = "summary-indicator";
        indicatorSyntax.className = "summary-indicator";
        indicatorSemantic.className = "summary-indicator";
        indicatorStatus.className = "summary-indicator";

        tokensCount.textContent = "0 Tokens";
        astCount.textContent = "0 AST Nodes";
        symbolCount.textContent = "0 Symbols";
        errorCount.textContent = "0 Errors";
        errorsTabBadge.style.display = "none";

        verdictBanner.className = "alert alert-info";
        verdictBanner.innerHTML = "<strong>Ready to Analyze.</strong> Click the 'Analyze Code' button to run lexical, syntax, and semantic checks.";

        errorsContainer.innerHTML = '<div class="empty-state">No errors detected. Ready for analysis.</div>';
        tokensTable.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No tokens generated yet. Click "Analyze Code".</td></tr>';
        astContainer.innerHTML = '<div class="empty-state">Parse tree / AST will appear here after analysis.</div>';
        derivationLog.innerHTML = '<span class="text-muted">Run analysis to see production rules invoked during recursive descent.</span>';
        symbolTable.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Symbol table will be populated upon semantic analysis.</td></tr>';
    }

    // ---------------- Grammar Modal ----------------

    btnGrammarModal.addEventListener("click", async () => {
        grammarModal.classList.add("active");
        try {
            const res = await fetch("/api/grammar");
            const data = await res.json();
            grammarCodeDisplay.textContent = data.ebnf;
        } catch (err) {
            grammarCodeDisplay.textContent = "Error loading grammar specifications.";
        }
    });

    btnModalClose.addEventListener("click", () => grammarModal.classList.remove("active"));
    btnModalOk.addEventListener("click", () => grammarModal.classList.remove("active"));
    grammarModal.addEventListener("click", (e) => {
        if (e.target === grammarModal) grammarModal.classList.remove("active");
    });

    // ---------------- Run Analysis ----------------

    async function runAnalysis() {
        const code = codeEditor.value;
        if (!code.trim()) {
            alert("Source code is empty. Please enter code or load a sample.");
            return;
        }

        btnAnalyze.disabled = true;
        btnAnalyze.innerHTML = "Analyzing...";

        try {
            const res = await fetch("/api/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ code })
            });

            const data = await res.json();
            currentAnalysisData = data;
            renderAnalysisResults(data);
        } catch (err) {
            console.error("Analysis request failed:", err);
            alert("Error communicating with compiler backend server.");
        } finally {
            btnAnalyze.disabled = false;
            btnAnalyze.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                Analyze Code
            `;
        }
    }

    btnAnalyze.addEventListener("click", runAnalysis);

    // ---------------- Render Results ----------------

    function renderAnalysisResults(data) {
        if (data.status === "EMPTY_CODE") {
            resetResults();
            return;
        }

        const summary = data.summary;
        const phaseStatus = data.phase_status;

        // 1. Update KPI Indicators
        statusLexical.textContent = phaseStatus.lexical;
        indicatorLexical.className = "summary-indicator " + (phaseStatus.lexical === "PASSED" ? "passed" : "failed");
        tokensCount.textContent = `${summary.token_count} Tokens`;

        statusSyntax.textContent = phaseStatus.syntax;
        indicatorSyntax.className = "summary-indicator " + (phaseStatus.syntax === "PASSED" ? "passed" : "failed");
        astCount.textContent = `${summary.ast_node_count} AST Nodes`;

        statusSemantic.textContent = phaseStatus.semantic;
        indicatorSemantic.className = "summary-indicator " + (phaseStatus.semantic === "PASSED" ? "passed" : "failed");
        symbolCount.textContent = `${summary.symbol_count} Symbols`;

        const isSuccess = data.status === "SUCCESS";
        finalVerdict.textContent = isSuccess ? "Compiled Successfully" : "Compilation Failed";
        indicatorStatus.className = "summary-indicator " + (isSuccess ? "passed" : "failed");
        errorCount.textContent = `${summary.total_errors} Errors (${summary.warnings_count} Warnings)`;

        // Update tab error badge
        if (summary.total_errors > 0) {
            errorsTabBadge.textContent = summary.total_errors;
            errorsTabBadge.style.display = "inline-block";
        } else {
            errorsTabBadge.style.display = "none";
        }

        // 2. Overview Banner
        if (isSuccess) {
            verdictBanner.className = "alert alert-success";
            verdictBanner.innerHTML = `
                <strong>✔ Compilation Succeeded!</strong> The MiniLang program passed Lexical, Syntax, and Semantic analysis with 0 errors. All symbols were verified in their respective scopes.
            `;
        } else {
            verdictBanner.className = "alert alert-danger";
            verdictBanner.innerHTML = `
                <strong>✖ Compilation Failed!</strong> Detected ${summary.total_errors} error(s) across compiler phases:
                ${summary.lexical_errors_count} Lexical, ${summary.syntax_errors_count} Syntax, ${summary.semantic_errors_count} Semantic.
            `;
        }

        // 3. Render Diagnostic Errors & Warnings
        renderDiagnostics(data);

        // 4. Render Tokens
        allTokens = data.tokens || [];
        applyTokenFilter(currentFilter);

        // 5. Render AST & Derivation
        renderAST(data.ast);
        renderDerivations(data.derivation_steps);

        // 6. Render Symbol Table
        renderSymbolTable(data.symbol_table);
    }

    function renderDiagnostics(data) {
        const lexErrors = data.lexical_errors || [];
        const synErrors = data.syntax_errors || [];
        const semErrors = data.semantic_errors || [];
        const warnings = data.warnings || [];

        const totalDiagnostics = lexErrors.length + synErrors.length + semErrors.length + warnings.length;

        if (totalDiagnostics === 0) {
            errorsContainer.innerHTML = '<div class="empty-state">✔ No errors or warnings detected in any compiler phase.</div>';
            return;
        }

        let html = "";

        // Lexical Errors
        lexErrors.forEach(err => {
            html += `
                <div class="error-item">
                    <div class="error-header-row">
                        <span class="badge badge-danger">Lexical Error</span>
                        <span class="error-loc">Line ${err.line}, Column ${err.column}</span>
                    </div>
                    <div class="error-msg">${escapeHtml(err.message)}</div>
                </div>
            `;
        });

        // Syntax Errors
        synErrors.forEach(err => {
            html += `
                <div class="error-item">
                    <div class="error-header-row">
                        <span class="badge badge-danger">Syntax Error</span>
                        <span class="error-loc">Line ${err.line}, Column ${err.column}</span>
                    </div>
                    <div class="error-msg">${escapeHtml(err.message)}</div>
                </div>
            `;
        });

        // Semantic Errors
        semErrors.forEach(err => {
            html += `
                <div class="error-item">
                    <div class="error-header-row">
                        <span class="badge badge-danger">Semantic Error (${err.error_type})</span>
                        <span class="error-loc">Line ${err.line}, Column ${err.column}</span>
                    </div>
                    <div class="error-msg">${escapeHtml(err.message)}</div>
                </div>
            `;
        });

        // Semantic Warnings
        warnings.forEach(w => {
            html += `
                <div class="error-item warning">
                    <div class="error-header-row">
                        <span class="badge badge-warning">Semantic Warning (${w.warning_type})</span>
                        <span class="error-loc">Line ${w.line}, Column ${w.column}</span>
                    </div>
                    <div class="error-msg">${escapeHtml(w.message)}</div>
                </div>
            `;
        });

        errorsContainer.innerHTML = html;
    }

    // ---------------- Tokens Table & Filters ----------------

    function applyTokenFilter(category) {
        currentFilter = category;
        const visibleTokens = allTokens.filter(t => {
            if (t.type === "EOF") return false;
            if (category === "all") return true;
            return t.category.toLowerCase() === category.toLowerCase();
        });

        filteredTokenCount.textContent = `Showing ${visibleTokens.length} of ${allTokens.length - 1} tokens`;

        if (visibleTokens.length === 0) {
            tokensTable.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No tokens match selected filter.</td></tr>';
            return;
        }

        let html = "";
        visibleTokens.forEach((t, idx) => {
            let catBadge = "badge-neutral";
            if (t.category === "Keyword") catBadge = "badge-info";
            else if (t.category === "Literal") catBadge = "badge-success";
            else if (t.category === "Operator") catBadge = "badge-warning";
            else if (t.category === "Identifier") catBadge = "badge-info";

            html += `
                <tr>
                    <td>${idx + 1}</td>
                    <td><code>${escapeHtml(t.type)}</code></td>
                    <td><span class="badge ${catBadge}">${escapeHtml(t.category)}</span></td>
                    <td><strong>${escapeHtml(t.value)}</strong></td>
                    <td>${t.line}</td>
                    <td>${t.column}</td>
                </tr>
            `;
        });
        tokensTable.innerHTML = html;
    }

    document.querySelectorAll(".filter-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            applyTokenFilter(btn.getAttribute("data-filter"));
        });
    });

    // ---------------- AST Tree Rendering ----------------

    function buildTreeNode(node) {
        if (!node) return "";
        const children = node.children || [];
        const hasChildren = children.length > 0;

        let html = '<div class="tree-node">';
        html += '<div class="tree-header">';
        if (hasChildren) {
            html += '<span class="tree-toggle">▼</span>';
        } else {
            html += '<span class="tree-toggle">•</span>';
        }
        html += `<span class="tree-node-label">${escapeHtml(node.label || node.node_type)}</span>`;
        if (node.line !== undefined) {
            html += `<span class="tree-node-detail">[L${node.line}:C${node.column}]</span>`;
        }
        html += '</div>';

        if (hasChildren) {
            html += '<div class="tree-children">';
            children.forEach(child => {
                html += buildTreeNode(child);
            });
            html += '</div>';
        }

        html += '</div>';
        return html;
    }

    function renderAST(ast) {
        if (!ast) {
            astContainer.innerHTML = '<div class="empty-state">No syntax tree available (Check syntax errors).</div>';
            return;
        }

        astContainer.innerHTML = buildTreeNode(ast);

        // Add toggle handlers
        astContainer.querySelectorAll(".tree-header").forEach(header => {
            header.addEventListener("click", () => {
                const childrenContainer = header.nextElementSibling;
                const toggle = header.querySelector(".tree-toggle");
                if (childrenContainer && childrenContainer.classList.contains("tree-children")) {
                    if (childrenContainer.style.display === "none") {
                        childrenContainer.style.display = "block";
                        toggle.textContent = "▼";
                    } else {
                        childrenContainer.style.display = "none";
                        toggle.textContent = "▶";
                    }
                }
            });
        });
    }

    document.getElementById("btnExpandAst").addEventListener("click", () => {
        astContainer.querySelectorAll(".tree-children").forEach(el => el.style.display = "block");
        astContainer.querySelectorAll(".tree-toggle").forEach(el => {
            if (el.textContent === "▶") el.textContent = "▼";
        });
    });

    document.getElementById("btnCollapseAst").addEventListener("click", () => {
        astContainer.querySelectorAll(".tree-children").forEach(el => el.style.display = "none");
        astContainer.querySelectorAll(".tree-toggle").forEach(el => {
            if (el.textContent === "▼") el.textContent = "▶";
        });
    });

    function renderDerivations(steps) {
        if (!steps || steps.length === 0) {
            derivationLog.innerHTML = '<span class="text-muted">No derivation steps logged.</span>';
            return;
        }
        let html = '<ol style="padding-left: 1.25rem;">';
        steps.forEach(s => {
            html += `<li><code>${escapeHtml(s)}</code></li>`;
        });
        html += '</ol>';
        derivationLog.innerHTML = html;
    }

    // ---------------- Symbol Table Rendering ----------------

    function renderSymbolTable(symbols) {
        if (!symbols || symbols.length === 0) {
            symbolTable.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No symbols declared.</td></tr>';
            symbolScopeCount.textContent = "Scopes: 0";
            return;
        }

        // Count unique scopes
        const uniqueScopes = new Set(symbols.map(s => s.scope_name));
        symbolScopeCount.textContent = `Unique Scopes: ${uniqueScopes.size}`;

        let html = "";
        symbols.forEach(sym => {
            const initBadge = sym.initialized === "Yes" ? "badge-success" : "badge-warning";
            html += `
                <tr>
                    <td><strong>${escapeHtml(sym.name)}</strong></td>
                    <td><span class="badge badge-info">${escapeHtml(sym.type)}</span></td>
                    <td><code>${escapeHtml(sym.scope_name)}</code></td>
                    <td>Level ${sym.scope_level}</td>
                    <td>Line ${sym.line}:${sym.column}</td>
                    <td><span class="badge ${initBadge}">${sym.initialized}</span></td>
                    <td><code>${escapeHtml(sym.value_preview)}</code></td>
                </tr>
            `;
        });
        symbolTable.innerHTML = html;
    }

    // ---------------- Export JSON Report ----------------

    btnExportJson.addEventListener("click", () => {
        if (!currentAnalysisData) {
            alert("Please analyze a program first before exporting.");
            return;
        }
        const jsonStr = JSON.stringify(currentAnalysisData, null, 2);
        const blob = new Blob([jsonStr], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `compiler_analysis_report_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    });

    // ---------------- Utility ----------------

    function escapeHtml(text) {
        if (text === null || text === undefined) return "";
        return String(text)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Initialize
    updateLineNumbers();
    loadSamplesList().then(() => {
        // Pre-load valid factorial sample on initial page load!
        selectSample("valid_factorial");
    });
});
