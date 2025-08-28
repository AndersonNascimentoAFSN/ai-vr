#!/usr/bin/env python3
"""
Script para backup e restore do banco de dados SQLite3 do sistema de VR/VA
"""

import sqlite3
import os
import shutil
from datetime import datetime
import zipfile

class VRDatabaseBackup:
    def __init__(self, db_path="vr_database.db"):
        """Inicializa o sistema de backup"""
        self.db_path = db_path
        self.backup_dir = "backups"
        
        # Criar diretório de backup se não existir
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            
    def create_backup(self, include_data=True):
        """Cria backup do banco de dados"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Banco de dados não encontrado: {self.db_path}")
            
        # Nome do arquivo de backup com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"vr_database_backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        print(f"💾 Criando backup: {backup_name}")
        
        if include_data:
            # Backup completo (cópia do arquivo)
            backup_file = f"{backup_path}.db"
            shutil.copy2(self.db_path, backup_file)
            print(f"✅ Backup completo criado: {backup_file}")
        else:
            # Backup apenas do schema (SQL)
            backup_file = f"{backup_path}.sql"
            self._backup_schema(backup_file)
            print(f"✅ Backup do schema criado: {backup_file}")
            
        # Criar arquivo ZIP com informações adicionais
        zip_file = f"{backup_path}.zip"
        self._create_backup_zip(backup_file, zip_file, timestamp)
        
        return backup_file
        
    def _backup_schema(self, backup_file):
        """Cria backup apenas do schema SQL"""
        conn = sqlite3.connect(self.db_path)
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            # Escrever informações do backup
            f.write(f"-- Backup do banco de dados VR/VA\n")
            f.write(f"-- Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"-- Arquivo original: {self.db_path}\n\n")
            
            # Escrever schema
            for line in conn.iterdump():
                f.write(f"{line}\n")
                
        conn.close()
        
    def _create_backup_zip(self, backup_file, zip_file, timestamp):
        """Cria arquivo ZIP com backup e informações"""
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Adicionar arquivo de backup
            zipf.write(backup_file, os.path.basename(backup_file))
            
            # Adicionar informações do backup
            info_content = f"""BACKUP DO BANCO DE DADOS VR/VA
Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Arquivo original: {self.db_path}
Tamanho original: {os.path.getsize(self.db_path):,} bytes
Versão: 1.0

INSTRUÇÕES DE RESTORE:
1. Extrair o arquivo ZIP
2. Usar o arquivo .db para restore completo
3. Ou usar o arquivo .sql para restore do schema

Para restaurar:
python3 database_backup.py --restore <arquivo_backup>
"""
            
            zipf.writestr("INFO_BACKUP.txt", info_content)
            
        print(f"📦 Arquivo ZIP criado: {zip_file}")
        
    def list_backups(self):
        """Lista todos os backups disponíveis"""
        print("📋 BACKUPS DISPONÍVEIS")
        print("=" * 50)
        
        if not os.path.exists(self.backup_dir):
            print("Nenhum backup encontrado.")
            return []
            
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.endswith('.zip'):
                file_path = os.path.join(self.backup_dir, file)
                file_size = os.path.getsize(file_path)
                mod_time = os.path.getmtime(file_path)
                mod_date = datetime.fromtimestamp(mod_time)
                
                backups.append({
                    'file': file,
                    'path': file_path,
                    'size': file_size,
                    'date': mod_date
                })
                
        # Ordenar por data (mais recente primeiro)
        backups.sort(key=lambda x: x['date'], reverse=True)
        
        if not backups:
            print("Nenhum backup encontrado.")
        else:
            for i, backup in enumerate(backups, 1):
                print(f"{i}. {backup['file']}")
                print(f"   📅 {backup['date'].strftime('%d/%m/%Y %H:%M:%S')}")
                print(f"   📏 {backup['size']:,} bytes ({backup['size']/1024/1024:.2f} MB)")
                print()
                
        return backups
        
    def restore_backup(self, backup_file):
        """Restaura backup do banco de dados"""
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Arquivo de backup não encontrado: {backup_file}")
            
        print(f"🔄 Restaurando backup: {backup_file}")
        
        # Verificar se é arquivo ZIP
        if backup_file.endswith('.zip'):
            # Extrair arquivo ZIP
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                # Procurar por arquivo .db ou .sql
                db_file = None
                for file_info in zipf.filelist:
                    if file_info.filename.endswith('.db'):
                        db_file = file_info.filename
                        break
                    elif file_info.filename.endswith('.sql'):
                        db_file = file_info.filename
                        break
                        
                if not db_file:
                    raise ValueError("Nenhum arquivo de banco encontrado no ZIP")
                    
                # Extrair arquivo
                zipf.extract(db_file, self.backup_dir)
                backup_file = os.path.join(self.backup_dir, db_file)
                
        # Fazer backup do banco atual se existir
        if os.path.exists(self.db_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup = f"vr_database_current_{timestamp}.db"
            shutil.copy2(self.db_path, os.path.join(self.backup_dir, current_backup))
            print(f"💾 Backup do banco atual criado: {current_backup}")
            
        # Restaurar banco
        if backup_file.endswith('.sql'):
            # Restaurar schema
            self._restore_schema(backup_file)
        else:
            # Restaurar arquivo completo
            shutil.copy2(backup_file, self.db_path)
            
        print(f"✅ Backup restaurado com sucesso!")
        
    def _restore_schema(self, schema_file):
        """Restaura apenas o schema SQL"""
        # Remover banco atual
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
        # Criar novo banco
        conn = sqlite3.connect(self.db_path)
        
        # Executar schema
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = f.read()
            
        conn.executescript(schema)
        conn.close()
        
    def cleanup_old_backups(self, keep_days=30):
        """Remove backups antigos"""
        print(f"🧹 Removendo backups com mais de {keep_days} dias...")
        
        if not os.path.exists(self.backup_dir):
            print("Nenhum backup para limpar.")
            return
            
        cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        removed_count = 0
        
        for file in os.listdir(self.backup_dir):
            file_path = os.path.join(self.backup_dir, file)
            if os.path.isfile(file_path):
                file_time = os.path.getmtime(file_path)
                if file_time < cutoff_date:
                    os.remove(file_path)
                    removed_count += 1
                    print(f"🗑️ Removido: {file}")
                    
        print(f"✅ {removed_count} backups antigos removidos.")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de Backup do Banco de Dados VR/VA')
    parser.add_argument('--backup', action='store_true', help='Criar backup')
    parser.add_argument('--restore', type=str, help='Restaurar backup (arquivo)')
    parser.add_argument('--list', action='store_true', help='Listar backups')
    parser.add_argument('--cleanup', type=int, metavar='DAYS', help='Limpar backups antigos (dias)')
    parser.add_argument('--schema-only', action='store_true', help='Backup apenas do schema')
    
    args = parser.parse_args()
    
    backup_system = VRDatabaseBackup()
    
    try:
        if args.backup:
            backup_system.create_backup(include_data=not args.schema_only)
        elif args.restore:
            backup_system.restore_backup(args.restore)
        elif args.list:
            backup_system.list_backups()
        elif args.cleanup:
            backup_system.cleanup_old_backups(args.cleanup)
        else:
            print("🗄️ SISTEMA DE BACKUP - BANCO DE DADOS VR/VA")
            print("=" * 60)
            print("Uso:")
            print("  python3 database_backup.py --backup          # Criar backup completo")
            print("  python3 database_backup.py --backup --schema-only  # Backup apenas schema")
            print("  python3 database_backup.py --restore <arquivo>     # Restaurar backup")
            print("  python3 database_backup.py --list            # Listar backups")
            print("  python3 database_backup.py --cleanup 30      # Limpar backups > 30 dias")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
