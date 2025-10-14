from django.db import migrations, models
import django.db.models.deletion


def map_text_to_category(apps, schema_editor):
    Registrant = apps.get_model("summitPage", "Registrant")
    Category = apps.get_model("summitPage", "Category")

    # Cache existing categories by lowercase name
    existing = {c.name.lower(): c for c in Category.objects.all()}

    for r in Registrant.objects.all():
        if isinstance(r.category_text, str) and r.category_text.strip():
            name = r.category_text.strip().lower()
            if name not in existing:
                # Create missing category
                existing[name] = Category.objects.create(name=r.category_text.strip().title())
            r.category = existing[name]
            r.save()


class Migration(migrations.Migration):

    dependencies = [
        ('summitPage', '0012_alter_registrant_category'),
    ]

    operations = [
        # 1️⃣ Rename old text field
        migrations.RenameField(
            model_name='registrant',
            old_name='category',
            new_name='category_text',
        ),

        # 2️⃣ Add the new FK field
        migrations.AddField(
            model_name='registrant',
            name='category',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='summitPage.category',
                verbose_name='Registration Category'
            ),
        ),

        # 3️⃣ Map text data to new FK
        migrations.RunPython(map_text_to_category),

        # 4️⃣ Drop old text field
        migrations.RemoveField(
            model_name='registrant',
            name='category_text',
        ),
    ]
