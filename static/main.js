/**
 * ニュース要約ページのフロント処理。
 * jQuery を使い、フォーム送信・要約結果描画・Markdown ダウンロードを制御する。
 */
let currentSummary = '';
let mermaidDiagrams = [];

$(function () {
    const $newsInput = $('#newsInput');
    const $summaryOutput = $('#summaryOutput');
    const $summarizeBtn = $('#summarizeBtn');
    const $downloadBtn = $('#downloadBtn');
    const $downloadDiagramBtn = $('#downloadDiagramBtn');

    const setLoadingView = () => {
        $summaryOutput.html(`
            <div class="loading">
                <div class="spinner"></div>
                <div class="loading-text">要約を生成中...</div>
            </div>
        `);
    };

    const resetButtons = () => {
        $summarizeBtn.prop('disabled', false);
        $downloadBtn.prop('disabled', !currentSummary);
        $downloadDiagramBtn.prop('disabled', mermaidDiagrams.length === 0);
    };

    async function summarize() {
        const newsText = $newsInput.val().trim();

        if (!newsText) {
            $summaryOutput.html('<div class="error">ニュースの本文を入力してください</div>');
            return;
        }

        setLoadingView();
        $summarizeBtn.prop('disabled', true);
        $downloadBtn.prop('disabled', true);
        $downloadDiagramBtn.prop('disabled', true);

        try {
            const data = await $.ajax({
                url: '/summarize',
                method: 'POST',
                contentType: 'application/json',
                dataType: 'json',
                data: JSON.stringify({ news_text: newsText }),
                processData: false
            });

            currentSummary = data.summary || '';
            $summaryOutput.html(marked.parse(currentSummary));
            $downloadBtn.prop('disabled', !currentSummary);

            try {
                const extractData = await $.ajax({
                    url: '/extract-mermaid',
                    method: 'POST',
                    contentType: 'application/json',
                    dataType: 'json',
                    data: JSON.stringify({ summary: currentSummary }),
                    processData: false
                });

                mermaidDiagrams = extractData.mermaid_diagrams || [];

                if (mermaidDiagrams.length > 0) {
                    $downloadDiagramBtn
                        .prop('disabled', false)
                        .text('Mermaid Editor を開く');
                }
            } catch (extractError) {
                console.error('Mermaid extraction failed', extractError);
            }
        } catch (error) {
            const message = error?.responseJSON?.error || error?.statusText || 'エラーが発生しました';
            $summaryOutput.html(`<div class="error">${message}</div>`);
        } finally {
            resetButtons();
        }
    }

    async function downloadMarkdown() {
        if (!currentSummary) {
            alert('要約がありません');
            return;
        }

        try {
            const blob = await $.ajax({
                url: '/download',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ summary: currentSummary }),
                processData: false,
                xhrFields: { responseType: 'blob' }
            });

            const url = window.URL.createObjectURL(blob);
            const $tempLink = $('<a>', {
                href: url,
                download: 'news_summary.md',
                style: 'display:none'
            }).appendTo('body');

            $tempLink[0].click();
            $tempLink.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            const message = error?.responseJSON?.error || 'エラーが発生しました';
            alert(message);
        }
    }

    function openMermaidLive() {
        window.open('https://mermaid.live/edit', '_blank');
    }

    $summarizeBtn.on('click', summarize);
    $downloadBtn.on('click', downloadMarkdown);
    $downloadDiagramBtn.on('click', openMermaidLive);

    $newsInput.on('keydown', function (e) {
        if (e.ctrlKey && e.key === 'Enter') {
            summarize();
        }
    });
});
