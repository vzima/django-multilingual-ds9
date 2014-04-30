#### 0.4.0 ####
 * Support Django 1.4 and 1.5.
 * Upgrade flatpages.
 * Change in flatpages database structure:

   ```sql
   ALTER TABLE "multilingual_flatpage_sites" RENAME COLUMN "multilingualflatpage_id" TO "flatpage_id";
   ```

 * Remove deprecated code from django-multilingual-ng.
 * Update styles for administation.

#### 0.3.1 ####
 * Refactor tests.
 * Change multilingual data keys in admin to avoid conflicts.

#### 0.3.0 ####
 * Support Django 1.4.
 * Move static files to `static` directory.
 * Fix multilingual model forms (#6).
 * Fix admin forms (#10). Include language into form.
