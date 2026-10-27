# 기기 자산과 타 기기 포팅

대상 사용자는 기존 리디 페이퍼 프로 사용자입니다. 코드 라이선스와 기기 자산의
취급은 `LICENSING.md`를 따릅니다. 기기 유래 파일에는 재사용 허락을 부여하지 않습니다.
타 기기 포팅에서는 아래 자산을 제외하고 자체 자료로 대체하세요.

| 저장소 | 제외·교체할 범위 |
|---|---|
| android-device | `stock-blobs/`의 waveform, `assets/bootanimation-stock-*.zip`, `sleep/`의 순정 이미지, `overlay/`와 `paper_launcher/`의 RIDI 유래 이미지·로고 |
| android-patches | 통합 패치에 포함된 RIDI 화면·아이콘 이미지. 메인의 JSON에 patch/target 경로를 열거 |
| sd-tools | `emmc-updater/assets/ram-header.bin`, `assets/tables/`의 기기 유래 템플릿 및 `runtime.zip` 내부의 기기별 구성. 타 기기용으로 복사해 사용하지 않음 |

위 경로 중 새로 작성한 소스 코드는 해당 코드 라이선스를 유지합니다. 전체 디렉터리를
일괄 독점 자산으로 지정하는 뜻은 아닙니다. 개별 파일과 출처 검토 목록은 메인 저장소의
[restricted-device-assets.json](https://github.com/INO-33/ridi-paper-pro/blob/checkpoint-20261016/restricted-device-assets.json),
[PUBLIC_ASSETS.md](https://github.com/INO-33/ridi-paper-pro/blob/checkpoint-20261016/PUBLIC_ASSETS.md)에 있습니다.

`wifi/rtl8189fs`와 대응 `.ko`는 GPL 드라이버, `RozhaOne.ttf`는 OFL 폰트입니다.
기기 유래 독점 자산으로 분류하지 않으며 각 라이선스 조건을 따릅니다.
`SystemWebView.apk`와 SD 런타임의 오픈소스 실행 파일도 각 구성 요소의 고지·대응 소스
요건을 따릅니다. 정확한 바이너리 재현이 확인되지 않은 항목은 공개 자산 검토에 남깁니다.

이 목록은 자동으로 파일을 제거하는 도구가 아닙니다. 현재 PAPER PRO 제품 정의는
필수 기기 자산을 계속 참조하므로 다른 기기 제품 정의에서 참조·오버레이도 교체해야 합니다.
