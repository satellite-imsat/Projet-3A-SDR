/**
  ******************************************************************************
  * @file    FatFs/FatFs_USBDisk/Src/main.c 
  * @author  MCD Application Team
  * @brief   Main program body
  *          This sample code shows how to use FatFs with USB disk drive.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2017 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "stdio.h"
#include "rtl-sdr.h"

/* Private typedef -----------------------------------------------------------*/
/* Private define ------------------------------------------------------------*/
/* Private macro -------------------------------------------------------------*/
/* Private variables ---------------------------------------------------------*/
FATFS USBDISKFatFs;           /* File system object for USB disk logical drive */
FIL MyFile;                   /* File object */
char USBDISKPath[4];          /* USB Host logical drive path */
extern rtlsdr_dev_t static_dev;
rtlsdr_dev_t *dev;
USBH_HandleTypeDef hUSBHost;
uint8_t usb_device_ready;
uint8_t OutPipe, InPipe;
volatile uint8_t* raw_buf_filling;

struct complex *buffer;
struct complex *demodBuffer;
struct complex *delayedBuffer;
int *output;



typedef enum {
  APPLICATION_IDLE = 0,  
  APPLICATION_START,    
  APPLICATION_RUNNING,
}MSC_ApplicationTypeDef;

MSC_ApplicationTypeDef Appli_state = APPLICATION_IDLE;

/* Private function prototypes -----------------------------------------------*/ 
static void SystemClock_Config(void);
static void Error_Handler(void);
static void MSC_Application(void);

/* Private functions ---------------------------------------------------------*/

/**
  * @brief  Main program
  * @param  None
  * @retval None
  */
int main(void)
{
  /* STM32F4xx HAL library initialization:
       - Configure the Flash prefetch, instruction and Data caches
       - Configure the Systick to generate an interrupt each 1 msec
       - Set NVIC Group Priority to 4
       - Global MSP (MCU Support Package) initialization
     */
  HAL_Init();

  
  /* Configure LED4 and LED5 */
  BSP_LED_Init(LED4);
  BSP_LED_Init(LED5);  
  
  /* Configure the system clock to 168 MHz */
  SystemClock_Config();
    
  /*##-1- Link the USB Host disk I/O driver ##################################*/
  if(FATFS_LinkDriver(&USBH_Driver, USBDISKPath) == 0)
  {
    /*##-2- Init Host Library ################################################*/
    USBH_Init(&hUSBHost, USBH_UserProcess, 0);

    /*##-3- Add Supported Class ##############################################*/
    USBH_RegisterClass(&hUSBHost, USBH_MSC_CLASS);

    /*##-4- Start Host Process ###############################################*/
    USBH_Start(&hUSBHost);

    /*##-5- Run Application (Blocking mode) ##################################*/
    while (1)
    {
      /* USB Host Background task */
      USBH_Process(&hUSBHost);

      if (hUSBHost.gState == HOST_CHECK_CLASS && !usb_device_ready) {

                  // attempt a connection on the control endpoint
                  // note: max packet size 64 bytes for FS and 512 bytes for HS
                  InPipe = USBH_AllocPipe(&hUSBHost, USB_PIPE_NUMBER);
                  USBH_StatusTypeDef status = USBH_OpenPipe(&hUSBHost,
                                              InPipe,
                                              USB_PIPE_NUMBER,
                                              hUSBHost.device.address,
                                              hUSBHost.device.speed,
                                              USB_EP_TYPE_BULK,
                                              USBH_MAX_DATA_BUFFER);

                  // continue connection attempt until successful
                  if (status == USBH_OK) {
                      usb_device_ready = 1;

                      MSC_Application();

                  }

              }
      /* Mass Storage Application State Machine */
      switch(Appli_state)
      {
      case APPLICATION_START:
        //MSC_Application();
        Appli_state = APPLICATION_IDLE;
        break;

      case APPLICATION_IDLE:
      default:
        break;
      }
    }
  }

  /* TrueStudio compilation error correction */
  while (1)
  {
  }
}

/**
  * @brief  Main routine for Mass Storage Class
  * @param  None
  * @retval None
  */
static void MSC_Application(void)
{
	//int sizeSignal = 4096;
	dev = &static_dev;
	 int8_t dongle_open = rtlsdr_open(&dev, 0);
	 int preamble_flag[32]={0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0};
	 dongle_open = rtlsdr_set_center_freq(dev, 162025000);
	 dongle_open = rtlsdr_set_tuner_gain_mode(dev,0); //0 : Automatique 1:Manuel
	 dongle_open = rtlsdr_set_sample_rate(dev, 960000);
	 dongle_open = rtlsdr_reset_buffer(dev);


	 while(1)
	 {
		 buffer = (struct complex*) malloc(sizeSignal*sizeof(struct complex));
		 delayedBuffer = (struct complex*) malloc(sizeSignal*sizeof(struct complex));
		 struct complex value;
	     dongle_open = rtlsdr_read_sync(dev, raw_buf_filling,2*sizeSignal , NULL);
	     if (dongle_open < 0)
	     {
	    	 BSP_LED_On(LED5);
	     }
	     for (int i = 0; i < sizeSignal; i++)
	     	 {
	    	 	 value.real = *(raw_buf_filling+2*i);
	    		 value.imag = *(raw_buf_filling+(2*i)+1);
	    		 *(buffer+i)= value;
	    	 }
	     output = (int*) malloc((sizeSignal/timeDelay-2)*sizeof(int));
	     //DEMODULATION
	     demodulate(buffer,delayedBuffer,output);
	     free(delayedBuffer);
	     free(buffer);
	     //TRAITEMENT
	     for(int i = 0; i<sizeSignal/timeDelay-2;i++)
	     {
	        int* bits = (int*) malloc(256*sizeof(int));
	        for(int j=0; j<256;j++){
	           *(bits+j)=*(output+i+j);
	        }
	        int currentSize=256;
	        nrziInv(bits, currentSize);
	        // Test the presence of the preamble flag in the signal
	        int present = 1;
	        for(int j=0; j<32;j++)
	        {
	            if(*(bits+j+8)!= *(preamble_flag+j))
	            {
	                   present = 0;
	            }
	         }
	         if(present == 0)
	         {
	        	 free(bits);
	         }
	         else {
	         // Treatment before decoding
	         currentSize -= sizePreambleFlag+sizeEndFlag;
	         int *withoutFlags = (int*) malloc((currentSize)*sizeof(int));
	         removePreambleFlag(bits,withoutFlags,currentSize);
	         free(bits);

	         int* bitStuffInv = (int*) malloc((currentSize)*sizeof(int));
	         currentSize= bitStuffingInv(withoutFlags,bitStuffInv,currentSize);
	         free(withoutFlags);

	         currentSize-=sizeCheckSum;
	         int *withoutChecksum = (int*) malloc((currentSize)*sizeof(int));
	         removeCheckSum(bitStuffInv,withoutChecksum,currentSize);
	         free(bitStuffInv);

	         currentSize = currentSize/8*8;
	         int *flipVector = (int*) malloc((currentSize)*sizeof(int));

	         flipBits(withoutChecksum, flipVector, currentSize);
	         free(withoutChecksum);
	         // Get infos in signal
	         int info;
	         info = getFromMessage(flipVector,0,6);
	           if(info != 1){
	              BSP_LED_On(LED4);
	           }
	         }
	     }
	     free(output);
	     continue;
	  }
	 rtlsdr_close(dev);
}

static void SystemClock_Config  (void)
{
  RCC_ClkInitTypeDef RCC_ClkInitStruct;
  RCC_OscInitTypeDef RCC_OscInitStruct;

  /* Enable Power Control clock */
  __HAL_RCC_PWR_CLK_ENABLE();
  
  /* The voltage scaling allows optimizing the power consumption when the device is 
     clocked below the maximum system frequency, to update the voltage scaling value 
     regarding system frequency refer to product datasheet.  */
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);
  
  /* Enable HSE Oscillator and activate PLL with HSE as source */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 8;
  RCC_OscInitStruct.PLL.PLLN = 336;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 7;
  HAL_RCC_OscConfig (&RCC_OscInitStruct);
  
  /* Select PLL as system clock source and configure the HCLK, PCLK1 and PCLK2 
     clocks dividers */
  RCC_ClkInitStruct.ClockType = (RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2);
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;  
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;  
  HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5);

  /* STM32F405x/407x/415x/417x Revision Z devices: prefetch is supported  */
  if (HAL_GetREVID() == 0x1001)
  {
    /* Enable the Flash prefetch */
    __HAL_FLASH_PREFETCH_BUFFER_ENABLE();
  }
}


/**
  * @brief  This function is executed in case of error occurrence.
  * @param  None
  * @retval None
  */
static void Error_Handler(void)
{
  /* Turn LED5 on */
  BSP_LED_On(LED5);
  while(1)
  {
  }
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t* file, uint32_t line)
{ 
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */

  /* Infinite loop */
  while (1)
  {
  }
}
#endif
