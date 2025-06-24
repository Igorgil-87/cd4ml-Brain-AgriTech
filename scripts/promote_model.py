import argparse
from app.mlflow_utils import promote_model_if_good_score

def main():
    parser = argparse.ArgumentParser(description="Promove modelo se R² for bom.")
    parser.add_argument("--model_name", required=True, help="Nome do modelo registrado no MLflow")
    parser.add_argument("--threshold", type=float, default=0.8, help="Threshold mínimo de R² para promover")

    args = parser.parse_args()

    try:
        promote_model_if_good_score(args.model_name, args.threshold)
        print(f"✅ Promoção avaliada para o modelo '{args.model_name}' com threshold {args.threshold}")
    except Exception as e:
        print(f"❌ Erro ao promover modelo: {e}")

if __name__ == "__main__":
    main()
