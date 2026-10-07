"""Single place that builds the SparkSession used by every stage."""
import os
import sys
from pathlib import Path

from pyspark.sql import SparkSession

from src import config

_BREW_JDK21 = Path("/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home")
_WIN_JDK_CANDIDATES = [
    Path(r"C:\Program Files\Microsoft\jdk-21.0.12.101-hotspot"),
    Path(r"C:\Program Files\Eclipse Adoptium"),
    Path(r"C:\Program Files\Java"),
    Path(r"C:\Program Files\Microsoft"),
]


def _ensure_java() -> None:
    """Spark is tested on LTS JDKs (17/21); auto-detect JDK and Hadoop on macOS & Windows."""
    if not os.environ.get("JAVA_HOME"):
        if _BREW_JDK21.exists():
            os.environ["JAVA_HOME"] = str(_BREW_JDK21)
        else:
            for cand in _WIN_JDK_CANDIDATES:
                if cand.is_dir():
                    if (cand / "bin" / "java.exe").exists():
                        os.environ["JAVA_HOME"] = str(cand)
                        break
                    # Search subdirectories for java.exe
                    subdirs = sorted(cand.glob("jdk*"), reverse=True)
                    for sub in subdirs:
                        if (sub / "bin" / "java.exe").exists():
                            os.environ["JAVA_HOME"] = str(sub)
                            break
                    if os.environ.get("JAVA_HOME"):
                        break

    # Auto-detect HADOOP_HOME on Windows if winutils is present
    if os.name == "nt" and not os.environ.get("HADOOP_HOME"):
        cand_hadoop = [
            Path(r"D:\MajorPRoject\hadoop"),
            config.ROOT / "hadoop",
            Path(r"C:\hadoop"),
        ]
        for h in cand_hadoop:
            if (h / "bin" / "winutils.exe").exists():
                os.environ["HADOOP_HOME"] = str(h)
                bin_str = str(h / "bin")
                if bin_str not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = bin_str + os.pathsep + os.environ.get("PATH", "")
                break

    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)


def get_spark(app_name: str = config.SPARK_APP_NAME, master: str = config.SPARK_MASTER,
              extra_conf: dict | None = None) -> SparkSession:
    _ensure_java()
    builder = SparkSession.builder.appName(app_name).master(master)
    for key, value in {**config.SPARK_CONF, **(extra_conf or {})}.items():
        builder = builder.config(key, value)
    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    return spark
