# 처음부터 개발환경 구축하기

이 문서는 7개 저장소에 접근할 수 있는 개발자를 위한 시작점입니다. Android 제품,
커널, WebView, SD 도구의 경로를 하나의 작업 폴더 아래에 구성합니다. 저장소를
공개로 전환하는 절차는 아닙니다. 자산 검토 기록은 [PUBLIC_ASSETS.md](PUBLIC_ASSETS.md)를 확인합니다.

기존 리디 페이퍼 프로 사용자를 위한 환경입니다. [LICENSING.md](LICENSING.md)의 코드 라이선스와
기기 자산 원칙을 확인하세요. 타 기기 포팅에서는 기기 유래 자료를 제외합니다.

## 1. 호스트와 공간

문서화한 호스트는 **Ubuntu 24.04 amd64 / Linux x86-64 / Python 3.10 이상**입니다.
기존 개발 PC의 환경을 기준으로 했으며, 새 OS에서 전체 빌드를 완료한 인증은 아닙니다.
Windows/macOS 사용자는 Linux VM을 준비합니다. SD GUI의 Windows 빌드는 별도입니다.
소스는 대소문자를 구분하고 심볼릭 링크·실행 권한을 보존하는 Linux 파일시스템에 둡니다.
공백 없는 절대 경로를 사용하세요. FAT/exFAT/NTFS 공유 폴더는 소스용으로 사용하지 않습니다.

계획용 여유 공간은 Android 소스·출력 **250 GiB 이상**, WebView까지 작업할 경우
**추가 150 GiB 이상**을 잡으세요. 이는 실측 최소치가 아닌 여유 예산입니다.
RAM은 16 GiB 이상을 계획하고 부족하면 병렬 수를 줄이세요. 실제 필요량은 대상과
동시 작업에 따라 달라집니다. 준비 검사의 기본 여유 공간 하한은 100 GiB이며,
통과가 전체 빌드 공간을 보장하지는 않습니다.

## 2. 기본 도구 설치와 메인 저장소 받기

```sh
sudo apt-get update
sudo apt-get install --no-install-recommends git gh python3 ca-certificates
git clone --branch checkpoint-20261016 https://github.com/INO-33/ridi-paper-pro.git "$HOME/ridi-manifest"
cd "$HOME/ridi-manifest"
python3 setup-host.py --profile all
```

마지막 명령은 설치할 패키지와 명령을 **출력만** 합니다. 검토 후 설치합니다.

```sh
python3 setup-host.py --profile all --install
```

`source`는 다운로드, `android`는 Android·커널, `sd`는 Linux SD GUI/도구용입니다.
`all`은 이 항목을 합칩니다. 필요한 패키지는 `host-packages.json`으로 관리합니다.
설치기는 시스템 Java/Python 대체 항목이나 Git 전역 설정을 바꾸지 않습니다.
원래 PC 전체 패키지 목록인 `host-environment.json`을 그대로 설치할 필요는 없습니다.

WebView 빌드는 별도로 [Docker Engine 공식 설치 안내](https://docs.docker.com/engine/install/ubuntu/)를
따라 Docker를 설치하고, 현재 사용자로 `docker info`가 성공하도록 준비합니다.
준비/빌드 스크립트 전체를 sudo로 실행하지 마세요. Docker 권한 설정은 해당 공식 안내를 따릅니다.

Android 8은 오래된 도구를 사용합니다. [AOSP 2.3–8.0 공식 안내](https://source.android.com/docs/setup/start/older-versions)는
당시 OS와 Java 8 요구를 설명합니다. 이 프로젝트의 Ubuntu 24.04 패키지와 호환 패치를
적용하는 절차는 이 문서를 기준으로 합니다. 최신 AOSP용 Java를 대신 쓰지 마세요.

## 3. Android·커널 소스 준비

새 작업 폴더를 지정합니다. 메인 저장소 폴더에서 실행합니다.

```sh
python3 check-host.py source "$HOME/ridi-workspace" --json "$HOME/ridi-host-source.json"
./prepare.sh "$HOME/ridi-workspace"
source "$HOME/ridi-workspace/env.sh"
python3 "$RIDI_MANIFEST_DIR/check-host.py" android "$RIDI_WORKSPACE" \
  --min-free-gb 25 --json "$RIDI_WORKSPACE/.orchestrator/logs/host-android.json"
"$ANDROID_BUILD_TOP/ridi-build-support/build.sh" check e70q10_reference-eng
```

`prepare.sh`는 고정 호환 라이브러리 준비, Repo 동기화, 23개 프로젝트 패치 적용, 작업 폴더 구성, 필수 자산과
600개 프로젝트 리비전/패치 결과 트리 검사를 순서대로 실행합니다. 어느 단계든 실패하면
그 지점에서 멈춥니다. Android/커널 컴파일과 기기 쓰기는 수행하지 않습니다.

결과 구조:

```text
ridi-workspace/
  env.sh
  android-sources/nxp-o8.0.0_1.0.0-ga/
    device/ridi/e70q10/                 기기 설정·앱 소스·필수 자산
    vendor/nxp-opensource/kernel_imx/   커널 소스
    ridi-android-changes/               통합 패치
    ridi-build-support/                개발 보조 도구
    ridi-sd-tools/                     SD 도구
  host-tools/, tools/, scripts/         개발 도구로 연결
  porting/                             SD 도구로 연결
  android-out/                         빌드 출력
  .orchestrator/logs/                   준비·검사·빌드 로그
```

Java 8은 보존한 JDK를, Python 2는 공식 Ubuntu 패키지에서 작업 폴더에 추출한
64비트 Python 2.7.18을 사용합니다. AOSP의 기본 Python 2에는 SSL 모듈이 없어
외부 준비 도구까지 다루기에는 부족합니다. 사전 검사는 SSL·zlib·ctypes·sqlite3·readline
import와 실제 실행을 확인합니다. 시스템 `/usr/bin/python`을 변경할 필요가 없습니다.
다른 구형 호스트 실행 파일용으로 `libc6-i386` 등 호환 패키지도 설치합니다.

구형 Clang 두 버전은 `libncurses.so.5`와 `libtinfo.so.5`도 요구합니다. Ubuntu 24.04의
동명 최신 개발 패키지만으로는 충족되지 않습니다. `prepare-host-libs.py`가 Ubuntu 공식
저장소의 지정 패키지와 Python 2 패키지를 SHA256 검증 후 `$RIDI_WORKSPACE/host-compat/`에만 추출합니다.
시스템 패키지에 구형 라이브러리를 설치하거나 다른 Ubuntu 저장소를 등록하지 않습니다.
버전·URL·해시는 `legacy-libraries.json`에 고정하며, `env.sh`가 라이브러리 경로를 설정합니다.
기존 작업 폴더를 갱신할 경우 `python3 prepare-host-libs.py "$RIDI_WORKSPACE"` 후
`python3 configure_workspace.py "$RIDI_WORKSPACE"`로 설정을 생성합니다. 기존 `env.sh`의
내용이 달라 거부되면 먼저 그 파일을 백업해 다른 이름으로 보존하고 다시 생성하세요.

## 4. 수정과 빌드

새 터미널마다 `source "$HOME/ridi-workspace/env.sh"`를 실행합니다.

```sh
export E70Q10_BUILD_JOBS=4
"$ANDROID_BUILD_TOP/ridi-build-support/build.sh" build e70q10_reference-eng kernelimage
python3 "$ANDROID_BUILD_TOP/ridi-build-support/build-wifi.py" --check
python3 "$ANDROID_BUILD_TOP/ridi-build-support/build-wifi.py"
export E70Q10_WIFI_MODULE="${E70Q10_OUT_DIR:-$RIDI_WORKSPACE/android-out/e70q10_reference}/wifi/8189fs.ko"
"$ANDROID_BUILD_TOP/ridi-build-support/build.sh" build e70q10_reference-eng bootimage systemimage vendorimage
```

기본 출력 루트는 `$RIDI_WORKSPACE/android-out/e70q10_reference`이고, 제품 이미지는
그 아래 `target/product/e70q10/`에 생성됩니다. `E70Q10_OUT_DIR`로 출력 루트를 바꿀 수 있습니다.
먼저 `kernelimage`를 만들고 대응 GPL Wi-Fi 소스로 모듈을 생성합니다. `build-wifi.py`는
소스 외부의 임시 복사본에서 모듈을 빌드하고 vermagic을 확인합니다. 커널을 바꾼 뒤에는
모듈을 다시 만들고 경로를 지정하세요. 기존 prebuilt의 ABI 일치를 가정하지 않습니다.
커널 변경도 이 제품의 `bootimage` 빌드에 반영됩니다. framework/gralloc 변경은
같은 빌드의 system/vendor를 함께 사용합니다. 이 명령은 플래시하지 않습니다.

Repo로 받은 프로젝트는 고정 리비전의 detached HEAD일 수 있습니다. 수정할 프로젝트에서
`git switch -c my-change`로 작업 브랜치를 만듭니다. Android 패치 대상의 수정은
해당 프로젝트에서 개발한 뒤 `ridi-android-changes`의 패치·해시·목표 트리를 갱신하고,
전용 저장소 변경은 해당 저장소에 커밋한 뒤 메인 lock과 manifest 핀을 갱신합니다.
`verify_checkout.py`는 원래 체크포인트와의 일치 검사이므로 개발 중인 변경은 불일치로
보고하는 것이 정상입니다. 개발 중인 소스에 `prepare.sh`를 다시 적용하지 않습니다.

에뮬레이터 제품 이름은 `e70q10_emulator-eng`, `e70q10_emulator_armv7-eng`입니다.
실행 안내는 기기 저장소의 `PAPER_EMULATOR.md`를 참고하며, 이 구축 절차는 에뮬레이터나
실기기를 시작하지 않습니다.

## 5. WebView 소스와 빌드

Android 환경 구성이 끝난 뒤 메인 폴더에서 실행합니다.

```sh
source "$HOME/ridi-workspace/env.sh"
cd "$RIDI_MANIFEST_DIR"
python3 check-host.py webview "$RIDI_WORKSPACE" \
  --json "$RIDI_WORKSPACE/.orchestrator/logs/host-webview.json"
python3 prepare-chromium.py "$RIDI_WORKSPACE"
"$RIDI_WORKSPACE/tools/chromium-m58-build/build_m58_xenial_arm.sh"
```

x86은 `build_m58_xenial_x86.sh`를 사용합니다. 준비는 고정 depot_tools의
Python 3/vpython3와 M58의 Python 2 hook 실행 경로를 함께 설정합니다. depot_tools의
Python 런타임과 Chromium SDK/NDK 등은 최초 실행 때 내려받습니다. 컴파일은 제공한
Ubuntu Xenial Dockerfile의 Java 8/Python 2/Bison 환경에서 실행합니다.

기본 출력은 `$CHROMIUM_SRC_ROOT/out/m58_xenial_arm` 또는 `m58_xenial_x86`입니다.
`M58_OUT_DIR`로 호스트 출력 폴더를 바꾸면 해당 폴더를 컨테이너에 연결합니다.
로그는 `$RIDI_WORKSPACE/.orchestrator/logs/`에 저장합니다.

빌더는 체크포인트 커밋과 깨끗한 소스를 기본으로 요구합니다. 개발자가 직접 만든
새 커밋을 빌드할 때 `M58_SOURCE_COMMIT`에 그 커밋을 지정합니다. 커밋 전 변경을
시험할 경우에만 `M58_ALLOW_DIRTY_SOURCE=1`을 사용하고 변경 내역을 따로 기록합니다.
재빌드한 APK를 Android 제품에 자동으로 교체하지는 않습니다.

## 6. SD GUI 개발

```sh
python3 "$RIDI_MANIFEST_DIR/check-host.py" sd "$RIDI_WORKSPACE" --min-free-gb 1
python3 "$ANDROID_BUILD_TOP/ridi-sd-tools/verify_assets.py"
python3 "$RIDI_WORKSPACE/porting/e70q10/emmc-tool/ridi_gui.py"
```

GUI 표시는 그래픽 세션이 필요합니다. `Tk import` 검사는 GUI 표시/기기 동작을
검증하지 않습니다. Windows EXE는 SD 저장소의 `WINDOWS_BUILD.md`를 따릅니다.
소스에 `runtime.zip`이 있으므로 이미 배포된 seed 패키지를 따로 찾을 필요 없이
`build_windows.py --app-dir`에 해당 소스 폴더를 지정할 수 있습니다. 새 RAM 런타임을
재생성하는 `build_gui_bundle.py`의 seed 패키지 경로는 별도 고급 절차입니다.

## 실패 시 확인할 곳

| 현상 | 확인/조치 |
|---|---|
| 호스트 검사 실패 | JSON 보고서의 누락 패키지·실행 실패 확인, `setup-host.py`로 설치 명령 확인 |
| GitHub 다운로드 실패 | 저장소 URL·네트워크 상태·GitHub 요청 제한 확인. 공개 소스 읽기에는 계정 인증 불필요 |
| 다운로드 중단 | `.orchestrator/logs/source-prepare-*.log` 확인. `prepare.sh`는 기존 소스 경로를 거부하므로 무작정 재실행하지 않음 |
| Python 실행 불가 | amd64 Linux와 32비트 호환 패키지 확인. 컨테이너/보안 정책이 32비트 실행을 막는지도 확인 |
| Docker 권한/데몬 오류 | 현재 사용자로 `docker info` 확인 |
| Chromium 준비 실패 | `chromium-source-prepare.log` 확인. 기존 checkout/depot_tools를 자동 삭제하거나 덮어쓰지 않음 |
| 빌드 실패 | `build-*.log` 또는 `chromium-m58-docker-*.log` 확인. 임의의 clean부터 실행하지 않음 |

네트워크 중단 후 복구가 필요하면 기존 로그와 작업 폴더를 보존합니다. 수정이 없는
다운로드 전용 폴더라면 새 목적지에서 다시 준비할 수 있습니다. 수동 Repo sync를
할 때에는 패치를 적용하기 전인지 확인해야 합니다. 패치 적용 후의 무조건적인 sync는
로컬 체크포인트와 개발 변경에 영향을 줄 수 있습니다.

## 검증 범위

설치 명령 생성, 사전 검사, 경로 구성, 오류 시 중단, 스크립트 구문과 고정 버전/자산
검사를 검증합니다. 새 호스트에서 수백 GB의 전체 다운로드와 Android/WebView 전체
빌드까지 완료했다는 의미는 아닙니다. 실기기 설치·물리 검증도 별도입니다.

2026-10-27 점검 결과: 25개 패치 복원·재적용과 호스트 런타임 실행 검사는 통과했습니다.
현재 점검 PC에서 미설치로 보고된 `lib32z1-dev`, `libelf-dev`, `fastboot`는 설치 목록에
포함되어 있습니다. 시스템 패키지 설치나 전체 컴파일은 이번 점검에서 수행하지 않았습니다.
상세 범위는 [development-validation.json](development-validation.json)을 확인합니다.
