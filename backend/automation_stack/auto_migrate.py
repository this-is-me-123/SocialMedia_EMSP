from automation_stack.database import Base, engine

if __name__ == "__main__":
    print("[auto_migrate] Creating all tables if not exist...")
    Base.metadata.create_all(bind=engine)
    print("[auto_migrate] Done.")
