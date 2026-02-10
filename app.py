import os
from flask import Flask

app = Flask(__name__)

# 파이썬 문법 오류 방지를 위해 f-string 대신 일반 문자열을 사용하고 스타일을 정비했습니다.
html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>재고 관리 시스템</title>
    <style>
        body { font-family: 'Malgun Gothic', sans-serif; background-color: #ffffff; display: flex; flex-direction: column; align-items: center; padding: 20px; color: #000; }
        .input-area { background: #fff; padding: 15px; border: 1px solid #000; border-radius: 4px; margin-bottom: 50px; width: 900px; text-align: center; }
        textarea { width: 95%; height: 100px; border: 1px solid #000; padding: 10px; margin-bottom: 10px; font-size: 12px; }
        button { padding: 10px 25px; background: #000; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
        
        /* 레이아웃 정밀 재설정 */
        .board-container { position: relative; margin-top: 60px; width: 840px; height: 240px; }
        .square-grid { display: grid; grid-template-columns: repeat(7, 120px); grid-template-rows: repeat(2, 120px); border: 2.5px solid #000; background: #fff; position: absolute; top: 0; left: 0; z-index: 1; }
        .square { border: 1px solid #000; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; text-align: center; height: 120px; box-sizing: border-box; background: #fff; }
        
        .round-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 3; }
        .round { 
            position: absolute; width: 85px; height: 85px; background: #fff; border: 2.5px solid #000; border-radius: 50%; 
            display: flex; flex-direction: column; justify-content: center; align-items: center; 
            transform: translate(-50%, -50%); text-align: center; pointer-events: auto;
        }

        .title { font-size: 11px; margin-bottom: 4px; width: 90%; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
        .val { font-size: 16px; font-weight: bold; margin-bottom: 15px; }
        .tank-id { font-size: 11px; font-weight: bold; border-top: 1px solid #000; width: 80%; padding-top: 2px; margin: 0 auto; }
        .square .tank-id { position: absolute; bottom: 8px; left: 10%; }

        .low-stock { background-color: #ffcccc !important; }
        .high-stock { background-color: #ccffcc !important; }
        
        .line-layer { position: absolute; top: 0; left: 0; width: 100%; height: 240px; z-index: 2; pointer-events: none; }
        .v-line { position: absolute; width: 2.5px; background: #000; height: 240px; top: 0; }
    </style>
</head>
<body>
    <div class="input-area">
        <strong>[재고 관리 시스템 - 최대 용량 2,000]</strong><br>
        <textarea id="excelData" placeholder="[탱크번호 원맥명 재고량] 순서로 붙여넣으세요"></textarea><br>
        <button onclick="applyMatchedData()">업데이트</button>
    </div>
    <div class="board-container">
        <div class="square-grid" id="grid"></div>
        <div class="line-layer" id="lines"></div>
        <div class="round-layer" id="overlay"></div>
    </div>
    <script>
        const MAX_CAPACITY = 2000;
        function getStockClass(val) {
            const num = parseFloat(String(val).replace(/,/g, ''));
            if (isNaN(num)) return '';
            if (num < MAX_CAPACITY * 0.2) return 'low-stock';
            if (num >= MAX_CAPACITY * 0.8) return 'high-stock';
            return '';
        }
        const squares = ['A201','A202','A203','A204','A205','A206','A207','A401','A402','A403','A404','A405','A406','A407'];
        const rounds = [['A101','A102','A103','A104','A105','A106'],['A301','A302','A303','A304','A305','A306'],['A501','A502','A503','A504','A505','A506']];
        
        squares.forEach(id => { 
            document.getElementById('grid').innerHTML += `<div class="square" id="tank-${id}"><div class="title" id="title-${id}">-</div><div class="val" id="val-${id}">-</div><div class="tank-id">${id}</div></div>`; 
        });
        
        for(let col=1; col<=6; col++) {
            const x = col * 120;
            document.getElementById('lines').innerHTML += `<div class="v-line" style="left:\${x}px;"></div>`;
            for(let row=0; row<3; row++) {
                const id = rounds[row][col-1];
                document.getElementById('overlay').innerHTML += `<div class="round" id="tank-${id}" style="left:\${x}px; top:\${row*120}px;"><div class="title" id="title-${id}">-</div><div class="val" id="val-${id}">-</div><div class="tank-id">${id}</div></div>`;
            }
        }

        function applyMatchedData() {
            const input = document.getElementById('excelData').value.trim();
            input.split('\\n').forEach(row => {
                const cols = row.split(/[\\t\\s]+/).filter(s => s.trim() !== "");
                if (cols.length >= 3) {
                    const tankId = cols[0].toUpperCase().trim();
                    const box = document.getElementById(\`tank-\${tankId}\`);
                    if (box) {
                        document.getElementById(\`title-\${tankId}\`).innerText = cols[1];
                        document.getElementById(\`val-\${tankId}\`).innerText = cols[2];
                        box.classList.remove('low-stock', 'high-stock');
                        const sc = getStockClass(cols[2]);
                        if(sc) box.classList.add(sc);
                    }
                }
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return html_content

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
