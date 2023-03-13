#include "trace.h"

void trace_itm_print(uint8_t channel, uint32_t data) {

    // send data with smallest possible channel buffer
    if (data > 0xFFFF) {
        while (!ITM->PORT[channel].u32 && (ITM->TCR & ITM_TCR_BUSY_Msk));

        ITM->PORT[channel].u32 = data;

    } else {
        if (data > 0xFF) {
            while (!ITM->PORT[channel].u16 && (ITM->TCR & ITM_TCR_BUSY_Msk));

            ITM->PORT[channel].u16 = data;

        } else {
            while (!ITM->PORT[channel].u8 && (ITM->TCR & ITM_TCR_BUSY_Msk));

            ITM->PORT[channel].u8 = data;
        }
    }
}

void trace_set_traps() {

    SCB->CCR |= 0x10; // DIV_0_TRP
    SCB->CCR |= 0x08; // UNALIGN_TRP
    CoreDebug->DEMCR |= 0x000007FE; // Vector catch enable

}

void trace_config() {

    CoreDebug->DEMCR |= 1 << 24;

    // unlock ITM/DWT
    ITM->LAR = 0xC5ACCE55;

    // Trace Control: disable ITM to adjust config
    ITM->TCR = 0;

    // wait for ITMBusy
    while (ITM->TCR & ITM_TCR_BUSY_Msk);

    // NRZ
    TPI->SPPR = 2;

    // re-enable ITM
    ITM->TCR |= 0x01;

    // enable all ports
    ITM->TER = 0xFFFFFFFF;

    // DWT cycle counter enable
    DWT->CTRL |= 0x01;

    // reset DWT clock
    DWT->CYCCNT = 0;

}

void trace_get_tgt_info(TargetInfo* t) {

    t->variant = (SCB->CPUID & SCB_CPUID_VARIANT_Msk) >> SCB_CPUID_VARIANT_Pos;
    t->revision = (SCB->CPUID & SCB_CPUID_REVISION_Msk) >> SCB_CPUID_REVISION_Pos;
    t->part_no = (SCB->CPUID & SCB_CPUID_PARTNO_Msk) >> SCB_CPUID_PARTNO_Pos;

}
