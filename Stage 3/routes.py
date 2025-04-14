# services/transaction/api/routes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..domain.models import Transaction, TransactionCreate
from ..domain.transaction_service import TransactionService
from ..api.dependencies import get_transaction_service, get_current_user

router = APIRouter()

@router.post("/transactions/", response_model=Transaction)
async def create_transaction(
    transaction: TransactionCreate,
    current_user = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    """Create a new transaction (sale, purchase, adjustment)."""
    # Ensure user has access to this store
    if not current_user.has_store_access(transaction.store_id):
        raise HTTPException(status_code=403, detail="Not authorized for this store")
        
    # Add user info to transaction
    transaction.created_by = current_user.id
    
    try:
        result = await service.create_transaction(transaction)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/transactions/", response_model=List[Transaction])
async def get_transactions(
    store_id: int,
    transaction_type: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 100,
    offset: int = 0,
    current_user = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    """Get transactions with filtering."""
    # Ensure user has access to this store
    if not current_user.has_store_access(store_id):
        raise HTTPException(status_code=403, detail="Not authorized for this store")
        
    transactions = await service.get_transactions(
        store_id=store_id,
        transaction_type=transaction_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    
    return transactions