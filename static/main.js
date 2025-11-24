let currentSummary = '';
let mermaidDiagrams = [];

/* ===========================================================
   要約処理
   =========================================================== */
async function summarize() {
    const newsText = document.getElementById('newsInput').value.trim();
    const outputDiv = document.getElementById('summaryOutput');
    const summarizeBtn = document.getElementById('summarizeBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const downloadDiagramBtn = document.getElementById('downloadDiagramBtn');

    if (!newsText) {
        outputDiv.innerHTML = '<div class="error">ニュースの本文を入力してください</div>';
        return;
    }

    outputDiv.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <div class="loading-text">要約を生成中...</div>
        </div>
    `;
    summarizeBtn.disabled = true;
    downloadBtn.disabled = true;
    downloadDiagramBtn.disabled = true;

    try {
        const response = await fetch('/summarize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ news_text: newsText })
        });

        const data = await response.json();

        if (response.ok) {
            currentSummary = data.summary;
            outputDiv.innerHTML = marked.parse(currentSummary);
            downloadBtn.disabled = false;

            // Mermaid 図解抽出
            const extractResponse = await fetch('/extract-mermaid', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ summary: currentSummary })
            });

            if (extractResponse.ok) {
                const extractData = await extractResponse.json();
                mermaidDiagrams = extractData.mermaid_diagrams;

                if (mermaidDiagrams.length > 0) {
                    downloadDiagramBtn.disabled = false;
                    downloadDiagramBtn.textContent = `Mermaid Editor を開く`;
                }
            }
        } else {
            outputDiv.innerHTML = `<div class="error">${data.error}</div>`;
        }

    } catch (error) {
        outputDiv.innerHTML = `<div class="error">エラーが発生しました: ${error.message}</div>`;
    } finally {
        summarizeBtn.disabled = false;
    }
}

/* ===========================================================
   Markdown ダウンロード
   =========================================================== */
async function downloadMarkdown() {
    if (!currentSummary) {
        alert('要約がありません');
        return;
    }

    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ summary: currentSummary })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'news_summary.md';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            const data = await response.json();
            alert(data.error);
        }
    } catch (error) {
        alert(`エラーが発生しました: ${error.message}`);
    }
}

/* ===========================================================
   Mermaid Editor を開くだけ
   =========================================================== */
function openMermaidLive() {
    window.open("https://mermaid.live/edit", "_blank");
}

/* ===========================================================
   Ctrl + Enter で要約実行
   =========================================================== */
document.getElementById('newsInput').addEventListener('keydown', function (e) {
    if (e.ctrlKey && e.key === 'Enter') {
        summarize();
    }
});
