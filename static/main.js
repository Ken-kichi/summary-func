
let currentSummary = '';
let mermaidDiagrams = [];

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
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ news_text: newsText })
        });

        const data = await response.json();

        if (response.ok) {
            currentSummary = data.summary;
            outputDiv.innerHTML = marked.parse(currentSummary);
            downloadBtn.disabled = false;

            // mermaid図解を抽出
            try {
                const extractResponse = await fetch('/extract-mermaid', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ summary: currentSummary })
                });

                if (extractResponse.ok) {
                    const extractData = await extractResponse.json();
                    mermaidDiagrams = extractData.mermaid_diagrams;
                    if (mermaidDiagrams.length > 0) {
                        downloadDiagramBtn.disabled = false;
                        // ボタンテキストを更新
                        if (mermaidDiagrams.length === 1) {
                            downloadDiagramBtn.textContent = '図をPNGで保存（1個）';
                        } else {
                            downloadDiagramBtn.textContent = `図をPNGで保存（${mermaidDiagrams.length}個）`;
                        }
                    }
                }
            } catch (error) {
                console.log('mermaid抽出エラー:', error);
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

async function downloadMarkdown() {
    if (!currentSummary) {
        alert('要約がありません');
        return;
    }

    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
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

function showDiagramMenu() {
    if (mermaidDiagrams.length === 0) {
        alert('mermaid図解がありません');
        return;
    }

    const diagramMenu = document.getElementById('diagramMenu');
    const container = document.getElementById('diagramButtonsContainer');

    // トグル表示
    if (diagramMenu.style.display === 'none') {
        diagramMenu.style.display = 'block';
        // ボタンを生成
        container.innerHTML = '';
        mermaidDiagrams.forEach((diagram, index) => {
            const btn = document.createElement('button');
            btn.className = 'diagram-btn';
            btn.textContent = `図解 ${index + 1} をダウンロード`;
            btn.onclick = () => downloadDiagramByIndex(index);
            container.appendChild(btn);
        });
    } else {
        diagramMenu.style.display = 'none';
    }
}

async function downloadDiagramByIndex(index) {
    if (index < 0 || index >= mermaidDiagrams.length) {
        alert('無効な図解インデックスです');
        return;
    }

    try {
        const response = await fetch('/convert-mermaid-png', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                mermaid_code: mermaidDiagrams[index],
                diagram_index: index
            })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `diagram_${index + 1}.png`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            // メニューを閉じる
            document.getElementById('diagramMenu').style.display = 'none';
        } else {
            const data = await response.json();
            alert(data.error);
        }
    } catch (error) {
        alert(`エラーが発生しました: ${error.message}`);
    }
}

document.getElementById('newsInput').addEventListener('keydown', function (e) {
    if (e.ctrlKey && e.key === 'Enter') {
        summarize();
    }
});
