import mlflow
import os

def promote_good_versions(model_name: str, threshold: float = 0.8):
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))
    client = mlflow.MlflowClient()

    versions = client.search_model_versions(f"name='{model_name}'")
    promoted = []

    for v in versions:
        version = v.version
        r2_score = float(v.metadata.get("r2_score", -1))

        if r2_score >= threshold:
            client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage="Production",
                archive_existing_versions=False  # não despromove outras
            )
            print(f"✅ Versão {version} promovida com R²={r2_score}")
            promoted.append(version)
        else:
            print(f"🔒 Versão {version} ignorada (R²={r2_score})")

    if not promoted:
        print("⚠️ Nenhuma versão elegível para promoção.")
        exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--threshold", type=float, default=0.8)
    args = parser.parse_args()

    promote_good_versions(args.model, args.threshold)