# RIDI PAPER PRO · Android 8

RIDI PAPER PRO(E70Q10)에 Android 8을 이식하는 프로젝트의 **메인 저장소**입니다.
NXP i.MX6SoloLite BSP와 Linux 4.9를 기반으로 E Ink 화면, 입력, 전원 관리,
RIDI용 시스템 UI와 WebView를 구성합니다. 이 저장소에서 전체 소스 조합과
준비·빌드 절차를 관리합니다.

현재 소스 체크포인트는 **2026-10-16**입니다. 소스는 아래 7개 비공개 저장소로
관리하며, manifest가 각 구성 요소의 정확한 커밋을 고정합니다.

## 저장소 구성

| 저장소 | 역할 |
|---|---|
| **[RIDI_ANDROID8_MANIFEST](https://github.com/INO-33/RIDI_ANDROID8_MANIFEST)** | **메인** · 전체 소스 버전, 준비 스크립트, 복원 검증 |
| [RIDI_PAPER_PRO_ANDROID8](https://github.com/INO-33/RIDI_PAPER_PRO_ANDROID8) | Linux 커널 · EPDC, 입력, 조명, PMIC·충전·배터리·RTC 드라이버 |
| [RIDI_PAPER_PRO_ANDROID8_DEVICE](https://github.com/INO-33/RIDI_PAPER_PRO_ANDROID8_DEVICE) | 기기 설정 · 제품 정의, RIDI 앱, 오버레이, 필수 기기 자산 |
| [RIDI_ANDROID8_CHANGES](https://github.com/INO-33/RIDI_ANDROID8_CHANGES) | Android 수정 통합 · 프레임워크, SurfaceFlinger, HAL, 시스템 앱 |
| [RIDI_CHROMIUM_M58](https://github.com/INO-33/RIDI_CHROMIUM_M58) | 커스텀 WebView · Chromium 58과 Breakpad·SwiftShader 변경 |
| [RIDI_ANDROID8_BUILD_TOOLS](https://github.com/INO-33/RIDI_ANDROID8_BUILD_TOOLS) | 개발·배포 도구 · 호스트 자산, Android·WebView 빌드 래퍼 |
| [RIDI_PAPER_PRO_SD_TOOLS](https://github.com/INO-33/RIDI_PAPER_PRO_SD_TOOLS) | SD/eMMC 전용 · CLI·GUI, RAM 도구, Windows 배포 빌더 |

과거에 개별 구성 요소로 나눴던 25개 저장소는 읽기 전용 보관본입니다.
현재 체크포인트의 소스 복원에는 위 7개 관리 저장소를 사용합니다.

## 대상과 소스 구조

| 항목 | 구성 |
|---|---|
| 기기 | RIDI PAPER PRO / Netronix E70Q10 |
| SoC | NXP i.MX6SoloLite / ARM |
| Android | Android 8.0 · NXP O8.0.0_1.0.0 GA 기반 |
| 커널 | Linux 4.9 기반 RIDI 기기 포트 |
| 화면 | EPDC E Ink · 기기 전용 waveform 사용 |
| 기본 빌드 대상 | `e70q10_reference-eng` |

Android 원본은 AOSP/NXP의 여러 프로젝트로 내려받습니다. RIDI 변경은 통합 패치로
적용하고, 커널·기기 설정은 전용 저장소에서 받습니다. 따라서 Android 내부의 Git
프로젝트 수와 직접 관리하는 GitHub 저장소 7개는 서로 다른 수치입니다.

## 소스 받기

Linux x86-64에서 Git, Python 3, GitHub CLI와 소스·빌드 출력용 디스크 공간이
필요합니다. 비공개 저장소를 읽을 수 있는 GitHub 계정으로 인증한 뒤 진행합니다.
준비 스크립트에는 Repo 실행기가 포함되어 있습니다.

```sh
gh auth status
gh auth setup-git
gh repo clone INO-33/RIDI_ANDROID8_MANIFEST ridi-manifest
cd ridi-manifest
./prepare.sh "$HOME/ridi-workspace"
source "$HOME/ridi-workspace/env.sh"
```

목적지는 새 작업 폴더로 지정합니다. 스크립트는 원본 리비전 동기화 → RIDI 변경
적용 → 자산 및 소스 트리 검증 → 작업 환경 설정 순서로 실행합니다. 기존 소스
폴더나 수정된 프로젝트를 덮어쓰지 않습니다. 실패 원인은 새 작업 폴더의
`.orchestrator/logs/`에 기록됩니다.

## Android 빌드

```sh
"$ANDROID_BUILD_TOP/ridi-build-support/build.sh" check e70q10_reference-eng
"$ANDROID_BUILD_TOP/ridi-build-support/build.sh" build e70q10_reference-eng bootimage systemimage vendorimage
```

Java 8 런타임과 Python 2 래퍼는 빌드 도구 저장소에서 제공합니다. 기본 출력은
`$RIDI_WORKSPACE/android-out/e70q10_reference/`입니다. 기존 출력 경로를 사용할 때는
`E70Q10_OUT_DIR`로 지정합니다. 프레임워크와 gralloc의 인터페이스가 함께 바뀐
체크포인트는 `system.img`와 `vendor.img`를 같은 빌드에서 준비하고, 커널 변경은
`boot.img` 및 vendor 모듈 호환성을 함께 확인합니다.

에뮬레이터 제품은 `e70q10_emulator-eng`, `e70q10_emulator_armv7-eng`입니다.
빌드 실행 자체가 기기 설치나 플래시를 수행하지는 않습니다.

## WebView와 업데이트 도구

- Android 제품 빌드는 기기 저장소의 고정된 WebView APK를 사용합니다. Chromium
  소스 재구성·별도 빌드는 [WebView 저장소](https://github.com/INO-33/RIDI_CHROMIUM_M58)를 확인하세요.
- SD/eMMC 도구와 Windows GUI 소스는 [SD 도구 저장소](https://github.com/INO-33/RIDI_PAPER_PRO_SD_TOOLS)의
  `porting/e70q10/emmc-tool/`에 있습니다. 업데이트·업그레이드·백업 범위는 해당
  `GUI_README.md`와 `README.md`를 확인합니다.
- 빌드 이미지와 전체 eMMC 백업은 별도 산출물로 보관합니다. Git에는 소스,
  필수 입력 자산과 그 해시를 보존합니다.

## 현재 상태와 검증 범위

이번 체크포인트는 최신 커널·전원 관리·절전/종료 화면·시스템 UI·배포 도구 소스를
보존합니다. 각 저장소의 커밋은 `release-lock.json`, Android 원본 버전은
`default.xml`, 통합 패치의 목표 소스 트리는 `RIDI_ANDROID8_CHANGES/projects.json`에
기록됩니다. 커밋/소스 트리/자산 해시 검증과 전체 제품의 실기기 검증은 구분합니다.

새 환경에서 Android·Chromium 전체 재빌드까지 검증한 릴리즈는 아닙니다. 특히
저전압 종료 직전 LOW BATTERY 자동 표시와 최종 전원 종료 전환은 추가 실기기
검증 항목입니다. 호스트 패키지, 오래된 Chromium 빌드 의존성과 원본 서버의
장기 보존도 별도 확인이 필요합니다. 원본 작업 소스 삭제는 전체 복원·빌드 검증을
마친 뒤 판단합니다.

기기 전용 자산을 포함하므로 7개 저장소의 비공개 설정을 유지합니다.
