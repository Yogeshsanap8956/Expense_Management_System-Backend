# Deploy backend

## Render (recommended for a live mandal)

Needs **Starter** (~$7/month) plus a **1 GB disk**. Free Render wipes SQLite and bill photos.

1. Add a payment method: https://dashboard.render.com  
2. New → **Blueprint** → connect GitHub repo `Expense_Management_System-Backend`.  
3. Branch: `feat/pwa-hosting`. Render reads `render.yaml`.  
4. Create. Wait until the service is Live.  
5. Open `https://mandal-api.onrender.com/health` (the hostname may differ; copy it from the service page).

You want `{"status":"ok",...}`.

Then set the frontend Worker env `VITE_API_BASE` to that origin (no trailing slash) and **rebuild** the frontend.

Login: `9999999999` / `admin123`.

Disk mount is `/data` (`mandal.db` + `uploads/`). Do not delete the disk.

## Oracle Always Free + Cloudflare Tunnel

Use this only if you have a Visa/Mastercard and want ₹0/month. See the previous Oracle steps: Ampere VM, Docker, then a Cloudflare tunnel to `http://api:8000`.
