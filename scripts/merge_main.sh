#!/bin/bash

# Skrypt automatyzujący łączenie bieżącej gałęzi z gałęzią main

# Sprawdzenie, na jakiej gałęzi jesteśmy
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Pracujesz na gałęzi: $CURRENT_BRANCH"

# Pobranie najnowszych zmian z repozytorium zdalnego
git fetch origin

# Próba scalenia z gałęzią main
if git merge origin/main; then
    echo "Scalanie przebiegło pomyślnie."
    # Wypchnięcie zmian na zdalne repozytorium
    git push origin "$CURRENT_BRANCH"
    echo "Zmiany zostały wysłane."
else
    echo "Wystąpiły konflikty podczas scalania!"
    echo "Pliki z konfliktami:"
    # Wyświetlenie plików z konfliktami
    git diff --name-only --diff-filter=U
    echo "Rozwiąż konflikty ręcznie, następnie wykonaj commit i push."
    exit 1
fi
