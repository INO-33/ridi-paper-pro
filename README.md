# RIDI PAPER PRO · Android 8

RIDI PAPER PRO(E70Q10)에 Android 8을 이식하는 프로젝트의 **메인 저장소**입니다.
NXP i.MX6SoloLite BSP와 Linux 4.9를 기반으로 E Ink 화면, 입력, 전원 관리,
RIDI용 시스템 UI와 WebView를 구성합니다. 이 저장소에서 전체 소스 조합과
준비·빌드 절차를 관리합니다.

## 개발 상태 안내

이 프로젝트는 **AI를 활용하여 개발**했습니다. 충분히 검증되지 않은 코드나 동작이
포함되어 있을 수 있으며, 사용 중 불안정한 동작·버그가 발생할 수 있습니다.
코드의 구조·가독성·일관성도 정리가 부족할 수 있습니다. 완성된 안정판으로 보장하지
않으므로, 사용·수정 전에 관련 소스와 알려진 검증 범위를 확인해 주세요.

현재 소스 체크포인트는 **2026-10-27**입니다. 소스는 아래 7개 공개 저장소로
관리하며, manifest가 각 구성 요소의 정확한 커밋을 고정합니다. 기존 링크 호환을 위해
기본 브랜치 이름 `checkpoint-20261016`은 유지하며 실제 기준일은 lock 파일을 따릅니다.

## 저장소 구성

| 저장소 | 역할 |
|---|---|
| **[ridi-paper-pro](https://github.com/INO-33/ridi-paper-pro)** | **메인** · 전체 소스 버전, 준비 스크립트, 복원 검증 |
| [ridi-paper-pro-linux-kernel](https://github.com/INO-33/ridi-paper-pro-linux-kernel) | Linux 커널 · EPDC, 입력, 조명, PMIC·충전·배터리·RTC 드라이버 |
| [ridi-paper-pro-android-device](https://github.com/INO-33/ridi-paper-pro-android-device) | 기기 설정 · 제품 정의, RIDI 앱, 오버레이, 필수 기기 자산 |
| [ridi-paper-pro-android-patches](https://github.com/INO-33/ridi-paper-pro-android-patches) | Android 수정 통합 · 프레임워크, SurfaceFlinger, HAL, 시스템 앱 |
| [ridi-paper-pro-webview](https://github.com/INO-33/ridi-paper-pro-webview) | 커스텀 WebView · Chromium 58과 Breakpad·SwiftShader 변경 |
| [ridi-paper-pro-dev-tools](https://github.com/INO-33/ridi-paper-pro-dev-tools) | 개발 보조 도구 · 호스트 자산, Android·WebView 빌드 래퍼 |
| [ridi-paper-pro-sd-tools](https://github.com/INO-33/ridi-paper-pro-sd-tools) | SD/eMMC 전용 · CLI·GUI, RAM 도구, Windows 배포 빌더 |

과거에 개별 구성 요소로 나눴던 25개 저장소는 통합 후 삭제했습니다.
현재 소스 복원과 변경 관리는 위 7개 저장소를 사용합니다.

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

처음 구성하는 개발자는 **[개발환경 구축 안내](DEVELOPMENT.md)**부터 따라갑니다.
호스트 패키지 설치, 사전 검사, 소스 준비, Android·커널·WebView·SD GUI 개발 순서를
설명합니다. 자산의 출처·검토 기록과 공개 결정은 **[공개 자산 목록](PUBLIC_ASSETS.md)**에 정리했습니다.

Linux x86-64에서 Git, Python 3, GitHub CLI와 소스·빌드 출력용 디스크 공간이
필요합니다. 공개 소스 다운로드에는 GitHub 계정 인증이 필요하지 않습니다.
준비 스크립트에는 Repo 실행기가 포함되어 있습니다.

```sh
git clone https://github.com/INO-33/ridi-paper-pro.git ridi-manifest
cd ridi-manifest
python3 setup-host.py --profile all --install
./prepare.sh "$HOME/ridi-workspace"
source "$HOME/ridi-workspace/env.sh"
```

목적지는 새 작업 폴더로 지정합니다. 스크립트는 원본 리비전 동기화 → RIDI 변경
적용 → 자산 및 소스 트리 검증 → 작업 환경 설정 순서로 실행합니다. 기존 소스
폴더나 수정된 프로젝트를 덮어쓰지 않습니다. 실패 원인은 새 작업 폴더의
`.orchestrator/logs/`에 기록됩니다.

## Android 빌드

`build.sh`는 실제 Python 2/Java 8/ARM 컴파일러 실행과 호스트 패키지 검사를 먼저 수행합니다.

```sh
"$ANDROID_BUILD_TOP/ridi-build-support/build.sh" check e70q10_reference-eng
"$ANDROID_BUILD_TOP/ridi-build-support/build.sh" build e70q10_reference-eng kernelimage
python3 "$ANDROID_BUILD_TOP/ridi-build-support/build-wifi.py" --check
python3 "$ANDROID_BUILD_TOP/ridi-build-support/build-wifi.py"
export E70Q10_WIFI_MODULE="${E70Q10_OUT_DIR:-$RIDI_WORKSPACE/android-out/e70q10_reference}/wifi/8189fs.ko"
"$ANDROID_BUILD_TOP/ridi-build-support/build.sh" build e70q10_reference-eng bootimage systemimage vendorimage
```

Java 8 런타임과 Python 2 래퍼는 빌드 도구 저장소에서 제공합니다. `prepare.sh`는
완전한 Python 2와 구형 Clang 호환 라이브러리도 작업 폴더에 준비합니다. 기본 출력은
`$RIDI_WORKSPACE/android-out/e70q10_reference/`입니다. 기존 출력 경로를 사용할 때는
`E70Q10_OUT_DIR`로 지정합니다. 프레임워크와 gralloc의 인터페이스가 함께 바뀐
체크포인트는 `system.img`와 `vendor.img`를 같은 빌드에서 준비하고, 커널 변경은
`boot.img` 및 vendor 모듈 호환성을 함께 확인합니다.

에뮬레이터 제품은 `e70q10_emulator-eng`, `e70q10_emulator_armv7-eng`입니다.
빌드 실행 자체가 기기 설치나 플래시를 수행하지는 않습니다.

## WebView와 업데이트 도구

- Android 제품 빌드는 기기 저장소의 고정된 WebView APK를 사용합니다. Chromium
  소스 재구성·별도 빌드는 [WebView 저장소](https://github.com/INO-33/ridi-paper-pro-webview)를 확인하세요.
- SD/eMMC 도구와 Windows GUI 소스는 [SD 도구 저장소](https://github.com/INO-33/ridi-paper-pro-sd-tools)의
  `porting/e70q10/emmc-tool/`에 있습니다. 업데이트·업그레이드·백업 범위는 해당
  `GUI_README.md`와 `README.md`를 확인합니다.
- 빌드 이미지와 전체 eMMC 백업은 별도 산출물로 보관합니다. Git에는 소스,
  필수 입력 자산과 그 해시를 보존합니다.

## 현재 상태와 검증 범위

이번 체크포인트는 최신 커널·전원 관리·절전/종료 화면·시스템 UI·배포 도구 소스를
보존합니다. 각 저장소의 커밋은 `release-lock.json`, Android 원본 버전은
`default.xml`, 통합 패치의 목표 소스 트리는 작업 소스의 `ridi-android-changes/projects.json`에
기록됩니다. 커밋/소스 트리/자산 해시 검증과 전체 제품의 실기기 검증은 구분합니다.

이번 점검에서 23개 Android 패치와 Chromium 의존성 2개의 복원·재적용, 기기·커널의
새 작업 폴더 복원, Java/Python2/컴파일러 실행을 확인했습니다. 자세한 범위는
[development-validation.json](development-validation.json)에 있습니다.

새 환경에서 Android·Chromium 전체 재빌드까지 검증한 릴리즈는 아닙니다. 특히
저전압 종료 직전 LOW BATTERY 자동 표시와 최종 전원 종료 전환은 추가 실기기
검증 항목입니다. 호스트 패키지, 오래된 Chromium 빌드 의존성과 원본 서버의
장기 보존도 별도 확인이 필요합니다. 원본 작업 소스 삭제는 전체 복원·빌드 검증을
마친 뒤 판단합니다.

2026-10-28 프로젝트 소유자의 승인에 따라 7개 저장소를 공개합니다. 자산 검토 목록의
항목도 포함하는 공개 결정이며, 기존 라이선스와 기기 유래 자산의 재사용 원칙은 유지합니다.
확인된 사실과 미검증 범위는 [자산 검토 기록](PUBLIC_ASSETS.md)에 보존합니다.


## 사용 대상과 라이선스

기존 **리디 페이퍼 프로 사용자**를 위한 프로젝트입니다. 새 자체 앱·보조 코드는
Apache 2.0이며 기존 파일은 원래 라이선스를 유지합니다. 기기 유래 파일에는 재사용
허락을 부여하지 않으며 타 기기 포팅에서는 해당 자료를 제외합니다.
[LICENSING.md](LICENSING.md), [DEVICE_ASSETS.md](DEVICE_ASSETS.md)를 확인하세요.
