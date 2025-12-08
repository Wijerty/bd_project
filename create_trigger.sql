CREATE OR REPLACE FUNCTION update_client_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE Client 
        SET 
            total_transactions = total_transactions + 1,
            total_amount_transferred = total_amount_transferred + NEW.amount,
            avg_transaction_amount = COALESCE((total_amount_transferred + NEW.amount) / (total_transactions + 1), NEW.amount),
            max_transaction_amount = GREATEST(COALESCE(max_transaction_amount, 0), NEW.amount)
        WHERE client_id = (SELECT client_id FROM Account WHERE account_id = NEW.sender_account_id);
        
        UPDATE Account 
        SET 
            transaction_count_today = transaction_count_today + 1,
            amount_transferred_today = amount_transferred_today + NEW.amount,
            last_transaction_date = NEW.transaction_date
        WHERE account_id = NEW.sender_account_id;
        
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_client_stats ON transaction;
CREATE TRIGGER trigger_update_client_stats
    AFTER INSERT ON transaction
    FOR EACH ROW
    EXECUTE FUNCTION update_client_stats();