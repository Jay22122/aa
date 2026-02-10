import os
from flask import Flask

app = Flask(__name__)

html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>재고 관리 시스템 (이력 관리)</title>
    <style>
        body { font-family: 'Malgun Gothic', sans-serif; background-color: #ffffff; display: flex; flex-direction: column; align-items: center; padding: 20px; color: #000; }
        .input-area { background: #fff; padding: 15px; border: 1px solid #000; border-radius: 4px; margin-bottom: 30px; width: 900px; text-align: center; }
        textarea { width: 95%; height: 80px; border: 1px solid #000; padding: 10px; margin-bottom: 10px; font-size: 12px; }
        .btn-group { display: flex; justify-content: center; gap: 10px; }
        button { padding: 10px 20px; background: #000; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
        button.history-btn { background: #555; }

        .board-container { position: relative; margin-top: 60px; width: 840px; height: 240px; margin-bottom: 50px; }
        .square-grid { display: grid; grid-template-columns: repeat(7, 120px); grid-template-rows: repeat(2, 120px); border: 2.5px solid #000; background: #fff; position: absolute; top: 0; left: 0; z-index: 1; }
        .square { border: 1px solid #000; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; text-align: center; height: 120px; box-sizing: border-box; background: #fff; }
        .round-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 3; }
        .round { position: absolute; width: 85px; height: 85px; background: #fff; border: 2.5px solid #000; border-radius: 50%; display: flex; flex-direction: column; justify-content: center; align-items: center; transform: translate(-50%, -50%); text-align: center; pointer-events: auto; }
        .title { font-size: 11px; margin-bottom: 4px; width: 90%; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
        .val { font-size: 16px; font-weight: bold; margin-bottom: 15px; }
        .tank-id { font-size: 11px; font-weight: bold; border-top: 1px solid #000; width: 80%; padding-top: 2px; margin: 0 auto; }
        .square .tank-id { position: absolute; bottom: 8px; left: 10%; }
        .low-stock { background-color: #ffcccc !important; }
        .high-stock { background-color: #ccffcc !important; }
        .line-layer { position: absolute; top: 0; left: 0; width: 100%; height: 240px; z-index: 2; pointer-events: none; }
        .v-line { position: absolute; width: 2.5px; background: #000; height: 240px; top: 0; }

        /* 히스토리 섹션 스타일 */
        .history-section { width: 900px; border-top: 2px dashed #ccc; padding-top: 20px; margin-top: 50px; }
        .history-list { display: flex; flex-direction: column; gap: 5px; max-height: 300px; overflow-y: auto; }
        .history-item { display: flex; justify-content: space-between; align-items: center; padding: 10px; border: 1px solid #eee; border-radius: 4px; cursor: pointer; }
        .history-item:hover { background: #f9f9f9; }
        .del-btn { background: #ff4d4d; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; font-size: 11px; }
    </style>
</head>
<body>
    <div class="input-area">
        <strong>[재고 관리 시스템 - 데이터 누적 기능 추가]</strong><br>
        <textarea id="excelData" placeholder="[탱크번호 원맥명 재고량] 순서로 붙여넣으세요"></textarea><br>
        <div class="btn-group">
            <button onclick="applyMatchedData()">현재 현황 업데이트</button>
            <button class="history-btn" onclick="clearHistory()">모든 기록 삭제</button>
        </div>
    </div>

    <div class="board-container">
        <div class="square-grid" id="grid"></div>
        <div class="line-layer" id="lines"></div>
        <div class="round-layer" id="overlay"></div>
    </div>

    <div class="history-section">
        <h3>기록 히스토리 (최근 순)</h3>
        <div id="historyList" class="history-list"></div>
    </div>

    <script>
        const MAX_CAPACITY = 2000;
        const squares = ['A201','A202','A203','A204','A205','A206','A207','A401','A402','A403','A404','A405','A406','A407'];
        const rounds = [['A101','A102','A103','A104','A105','A106'],['A301','A302','A303','A304','A305','A306'],['A501','A502','A503','A504','A505','A506']];
        
        // 도식 초기화
        function initBoard() {
            const gridDiv = document.getElementById('grid');
            gridDiv.innerHTML = '';
            squares.forEach(id => { 
                gridDiv.innerHTML += '<div class="square" id="tank-' + id + '"><div class="title" id="title-' + id + '">-</div><div class="val" id="val-' + id + '">-</div><div class="tank-id">' + id + '</div></div>'; 
            });
            const lineDiv = document.getElementById('lines');
            const overlayDiv = document.getElementById('overlay');
            lineDiv.innerHTML = ''; overlayDiv.innerHTML = '';
            for(let col=1; col<=6; col++) {
                const x = col * 120;
                lineDiv.innerHTML += '<div class="v-line" style="left:' + x + 'px;"></div>';
                for(let row=0; row<3; row++) {
                    const id = rounds[row][col-1];
                    overlayDiv.innerHTML += '<div class="round" id="tank-' + id + '" style="left:' + x + 'px; top:' + (row*120) + 'px;"><div class="title" id="title-' + id + '">-</div><div class="val" id="val-' + id + '">-</div><div class="tank-id">' + id + '</div></div>';
                }
            }
        }

        function getStockClass(val) {
            const num = parseFloat(String(val).replace(/,/g, ''));
            if (isNaN(num)) return '';
            if (num < MAX_CAPACITY * 0.2) return 'low-stock';
            if (num >= MAX_CAPACITY * 0.8) return 'high-stock';
            return '';
        }

        // 데이터 적용 및 저장
        function applyMatchedData() {
            const input = document.getElementById('excelData').value.trim();
            if (!input) return;
            const timestamp = new Date().toLocaleString();
            const snapshot = [];

            input.split('\\n').forEach(row => {
                const cols = row.split(/[\\t\\s]+/).filter(s => s.trim() !== "");
                if (cols.length >= 3) {
                    const tankId = cols[0].toUpperCase().trim();
                    const grainName = cols[1];
                    const stock = cols[2];
                    updateTankUI(tankId, grainName, stock);
                    snapshot.push({ tankId, grainName, stock });
                }
            });

            saveToHistory(timestamp, snapshot);
            renderHistoryList();
        }

        function updateTankUI(id, grain, stock) {
            const box = document.getElementById('tank-' + id);
            if (box) {
                document.getElementById('title-' + id).innerText = grain;
                document.getElementById('val-' + id).innerText = stock;
                box.classList.remove('low-stock', 'high-stock');
                const sc = getStockClass(stock);
                if(sc) box.classList.add(sc);
            }
        }

        // 로컬 스토리지 관리
        function saveToHistory(time, data) {
            let history = JSON.parse(localStorage.getItem('inventoryHistory') || '[]');
            history.unshift({ time, data }); // 최신이 위로
            localStorage.setItem('inventoryHistory', JSON.stringify(history.slice(0, 50))); // 최대 50개 유지
        }

        function renderHistoryList() {
            const history = JSON.parse(localStorage.getItem('inventoryHistory') || '[]');
            const listDiv = document.getElementById('historyList');
            listDiv.innerHTML = history.map((item, index) => `
                <div class="history-item">
                    <span onclick="loadHistory(${index})"><strong>${item.time}</strong> 기록 보기</span>
                    <button class="del-btn" onclick="deleteHistory(${index})">삭제</button>
                </div>
            `).join('');
        }

        function loadHistory(index) {
            const history = JSON.parse(localStorage.getItem('inventoryHistory') || '[]');
            const record = history[index];
            initBoard(); // 초기화 후 로드
            record.data.forEach(item => updateTankUI(item.tankId, item.grainName, item.stock));
            alert(record.time + ' 데이터가 로드되었습니다.');
        }

        function deleteHistory(index) {
            let history = JSON.parse(localStorage.getItem('inventoryHistory') || '[]');
            history.splice(index, 1);
            localStorage.setItem('inventoryHistory', JSON.stringify(history));
            renderHistoryList();
        }

        function clearHistory() {
            if(confirm('모든 기록을 삭제하시겠습니까?')) {
                localStorage.removeItem('inventoryHistory');
                renderHistoryList();
                initBoard();
            }
        }

        initBoard();
        renderHistoryList();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return html_content

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
