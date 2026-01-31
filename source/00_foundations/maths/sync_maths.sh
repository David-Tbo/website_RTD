#!/bin/bash

# Synchroniser le dossier Maths vers iCloud (version safe)

# Dossier source
SOURCE="/Users/davidtbo/Maths"

# Dossier destination iCloud
DEST="/Users/davidtbo/Library/Mobile Documents/com~apple~CloudDocs/Maths"

# Synchronisation avec rsync sans supprimer les fichiers dans iCloud
rsync -av --ignore-existing "$SOURCE/" "$DEST/"

# Mettre à jour les fichiers modifiés dans iCloud
rsync -avu "$SOURCE/" "$DEST/"

echo "Synchronisation safe terminée ✅"
