# scott-py

using python 3.10

# for teacher

- practices: 강의에서 진행하신 것들 테스트한 흔적
- chat: 프로젝트 mission 2 작업 결과물
- app: 프로젝트 mission 3 작업 결과물


# environment variables

app/.env 경로에 OPENAI_API_KEY를 넣어두어야 정상 작동됩니다.

```bash
export OPENAI_API_KEY="sk-xyz"
```

# run

pynecone의 새 이름인 reflex로 설치해보았습니다.

```bash
cd app

# python libs 설치
pip install -r requirements.txt

# reflex 환경 초기화
reflex init

# run
reflex run
```


# preprocess

reflex run이 되고 나면 자동으로 core 의 환경 초기화가 실행됩니다.
정상적으로 실행되고 나면 app/data/pre 폴더 내에 다음과 같은 파일들이 생성됩니다.

- 