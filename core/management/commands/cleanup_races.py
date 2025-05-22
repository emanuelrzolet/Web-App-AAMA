from django.core.management.base import BaseCommand
from core.models import RacaCachorro, RacaGato

class Command(BaseCommand):
    help = 'Clean up duplicate SRD races'

    def handle(self, *args, **options):
        # Clean up RacaCachorro
        srd_cachorro = RacaCachorro.objects.filter(nome="SRD")
        if srd_cachorro.count() > 1:
            main_srd = srd_cachorro.first()
            for other_srd in srd_cachorro[1:]:
                # Update any references to use the main SRD
                other_srd.cachorro_set.update(raca=main_srd)
                other_srd.delete()
            self.stdout.write(self.style.SUCCESS('Successfully cleaned up duplicate SRD for dogs'))

        # Clean up RacaGato
        srd_gato = RacaGato.objects.filter(nome="SRD")
        if srd_gato.count() > 1:
            main_srd = srd_gato.first()
            for other_srd in srd_gato[1:]:
                # Update any references to use the main SRD
                other_srd.gato_set.update(raca=main_srd)
                other_srd.delete()
            self.stdout.write(self.style.SUCCESS('Successfully cleaned up duplicate SRD for cats')) 