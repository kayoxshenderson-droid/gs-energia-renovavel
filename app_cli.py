"""Citizen Assist AI - modulo de energia (versao terminal).

Uso:  python app_cli.py
      python app_cli.py "quanto o chuveiro gasta?"   (pergunta unica)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
from energia.assistente import AssistenteEnergia, MENU  # noqa: E402


def main() -> None:
    bot = AssistenteEnergia()
    if len(sys.argv) > 1:
        print(bot.responder(" ".join(sys.argv[1:])))
        return
    print("=" * 70)
    print(" Citizen Assist AI | Energia no banho (digite 'sair' para encerrar)")
    print("=" * 70)
    print(MENU)
    while True:
        try:
            pergunta = input("\nVoce: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if pergunta.lower() in {"sair", "exit", "quit"}:
            break
        if pergunta:
            print("\nAssistente:\n" + bot.responder(pergunta))
    print("\nAte logo! Pequenas mudancas no banho ja fazem diferenca.")


if __name__ == "__main__":
    main()
