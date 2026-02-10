import os
from flask import Flask

app = Flask(__name__)

# [여기에 이전에 완성한 html_content 전체 내용을 복사해서 넣으세요]
html_content = """
from flask import Flask
from google.colab import output
import threading

app = Flask(__name__)

html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>재고 현황판 - 전체 탱크 연동</title>
    <style>
        body { font-family: 'Malgun Gothic', sans-serif; background-color: #ffffff; display: flex; flex-direction: column; align-items: center; padding: 20px; color: #000; }
        .input-area { background: #fff; padding: 15px; border: 1px solid #000; border-radius: 4px; margin-bottom: 50px; width: 950px; text-align: center; }
        textarea { width: 95%; height: 100px; border: 1px solid #000; padding: 10px; margin-bottom: 10px; font-size: 12px; }
        button { padding: 10px 25px; background: #000; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }

        .board-container { position: relative; margin-top: 60px; width: 840px; }
        .square-grid { display: grid; grid-template-columns: repeat(7, 120px); grid-template-rows: repeat(2, 120px); border: 2.5px solid #000; background: #fff; position: relative; z-index: 1; }
        .square { border: 1px solid #000; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; text-align: center; transition: background 0.3s; height: 120px; box-sizing: border-box;}
        
        .round-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 2; }
        .round { 
            position: absolute; width: 85px; height: 85px; background: #fff; border: 2.5px solid #000; border-radius: 50%; 
            display: flex; flex-direction: column; justify-content: center; align-items: center; transform: translate(-50%, -50%); transition: background 0.3s;
            pointer-events: auto; text-align: center;
        }

        .title { font-size: 11px; margin-bottom: 4px; width: 90%; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; font-weight: normal; }
        .val { font-size: 16px; font-weight: bold; margin-bottom: 5px; }
        .tank-id { font-size: 11px; font-weight: bold; border-top: 1px solid #000; width: 80%; padding-top: 2px; margin: 0 auto; }
        .square .tank-id { position: absolute; bottom: 8px; left: 10%; }

        .low-stock { background-color: #ffcccc !important; }
        .high-stock { background-color: #ccffcc !important; }
        
        .line-layer { position: absolute; top: 0; left: 0; width: 100%; height: 240px; z-index: 0; pointer-events: none; }
        .v-line { position: absolute; width: 2.5px; background: #000; height: 240px; }
    </style>
</head>
<body>

    <div class="input-area">
        <strong>[전체 탱크 데이터 매칭 - 최대 용량 2,000]</strong><br>
        <span style="font-size: 11px; color: #555;">엑셀에서 [탱크번호 / 원맥명 / 재고량] 영역을 복사해 붙여넣으세요.</span><br>
        <textarea id="excelData" placeholder="예: A104  호주산백밀  1250"></textarea><br>
        <button onclick="applyMatchedData()">데이터 매칭 업데이트</button>
    </div>

    <div class="board-container">
        <div class="line-layer" id="lines"></div>
        <div class="square-grid" id="grid"></div>
        <div class="round-layer" id="overlay"></div>
    </div>

    <script>
        const MAX_CAPACITY = 2000;

        function getStockClass(val) {
            if (!val || val === '-') return '';
            const num = parseFloat(String(val).replace(/,/g, ''));
            if (isNaN(num)) return '';
            if (num < MAX_CAPACITY * 0.2) return 'low-stock';
            if (num >= MAX_CAPACITY * 0.8) return 'high-stock';
            return '';
        }

        // 전체 탱크 리스트 정의
        const squares = ['A201','A202','A203','A204','A205','A206','A207','A401','A402','A403','A404','A405','A406','A407'];
        const rounds = [
            ['A101','A102','A103','A104','A105','A106'],
            ['A301','A302','A303','A304','A305','A306'],
            ['A501','A502','A503','A504','A505','A506']
        ];

        // 초기 화면 셋팅
        squares.forEach(id => {
            document.getElementById('grid').innerHTML += `
                <div class="square" id="tank-${id}">
                    <div class="title" id="title-${id}">-</div>
                    <div class="val" id="val-${id}">-</div>
                    <div class="tank-id">${id}</div>
                </div>`;
        });

        for(let col=1; col<=6; col++) {
            const x = col * 120;
            document.getElementById('lines').innerHTML += `<div class="v-line" style="left:${x}px;"></div>`;
            for(let row=0; row<3; row++) {
                const id = rounds[row][col-1];
                document.getElementById('overlay').innerHTML += `
                    <div class="round" id="tank-${id}" style="left:${x}px; top:${row*120}px;">
                        <div class="title" id="title-${id}">-</div>
                        <div class="val" id="val-${id}">-</div>
                        <div class="tank-id">${id}</div>
                    </div>`;
            }
        }

        function applyMatchedData() {
            const input = document.getElementById('excelData').value.trim();
            if(!input) return alert("데이터를 입력해주세요.");

            const rows = input.split('\\n');
            
            rows.forEach(row => {
                // 공백 또는 탭으로 구분된 데이터를 배열로 변환
                const cols = row.split(/[\\t\\s]{2,}|\\t/).filter(s => s.trim() !== "");
                
                // 만약 탭 구분이 안 될 경우를 대비해 일반 공백 하나로도 체크
                const finalCols = cols.length < 3 ? row.split(/[\\s]+/).filter(s => s.trim() !== "") : cols;

                if (finalCols.length >= 3) {
                    const tankId = finalCols[0].toUpperCase().replace(/\\s/g, ''); // 공백 제거
                    const grainName = finalCols[1];
                    const stockAmount = finalCols[2];

                    const titleElem = document.getElementById(`title-${tankId}`);
                    const valElem = document.getElementById(`val-${tankId}`);
                    const boxElem = document.getElementById(`tank-${tankId}`);

                    if (titleElem && valElem && boxElem) {
                        titleElem.innerText = grainName;
                        valElem.innerText = stockAmount;
                        
                        // 배경색 초기화 후 재설정
                        boxElem.classList.remove('low-stock', 'high-stock');
                        const sClass = getStockClass(stockAmount);
                        if(sClass) boxElem.classList.add(sClass);
                    }
                }
            });
            alert("데이터 매칭이 완료되었습니다.");
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return html_content

def run():
    app.run(port=8170)

threading.Thread(target=run).start()
output.serve_kernel_port_as_iframe(8170)
"""

@app.route('/')
def home():
    return html_content

if __name__ == "__main__":
    # 서버 포트 설정 (서버 환경에 맞게 자동 조절)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)