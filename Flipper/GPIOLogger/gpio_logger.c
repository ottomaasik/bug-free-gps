#include <furi.h>
#include <gui/gui.h>
#include <furi_hal.h>
#include <furi_hal_serial.h>
#include <furi/core/stream_buffer.h>
#include <furi/core/thread.h>
#include <storage/storage.h>
#include <dialogs/dialogs.h>
#include <input/input.h>

#define UART_BAUDRATE 115200
#define RX_BUF_SIZE 128
#define LOG_FILE_PATH "/ext/uart_log.txt"
#define APP_EXIT_FLAG (1 << 10)

static FuriThreadId main_thread_id;


typedef enum {
    WorkerEvtStop = (1 << 0),
    WorkerEvtRxDone = (1 << 1),
} WorkerEvtFlags;

typedef struct {
    FuriThread* rx_thread;
    FuriStreamBuffer* rx_stream;
    FuriHalSerialHandle* serial;
    File* file;
} UartLogger;

static void input_callback(InputEvent* event, void* context) {
    UNUSED(context);
    if(event->type == InputTypeShort && event->key == InputKeyBack) {
        furi_thread_flags_set(main_thread_id, APP_EXIT_FLAG);
    }
}


static void draw_callback(Canvas* canvas, void* context) {
    UNUSED(context);
    canvas_clear(canvas);
    canvas_set_font(canvas, FontPrimary);
    canvas_draw_str_aligned(canvas, 64, 32, AlignCenter, AlignCenter, "UART Logging...");
}

static void uart_rx_cb(FuriHalSerialHandle* handle, FuriHalSerialRxEvent event, void* context) {
    if(event == FuriHalSerialRxEventData) {
        UartLogger* logger = context;
        uint8_t byte = furi_hal_serial_async_rx(handle);
        furi_stream_buffer_send(logger->rx_stream, &byte, 1, 0);
        furi_thread_flags_set(furi_thread_get_id(logger->rx_thread), WorkerEvtRxDone);
    }
}

static int32_t uart_logger_worker(void* context) {
    UartLogger* logger = context;
    uint8_t rx_buf[RX_BUF_SIZE];

    while(1) {
        uint32_t flags = furi_thread_flags_wait(WorkerEvtStop | WorkerEvtRxDone, FuriFlagWaitAny, FuriWaitForever);
        if(flags & WorkerEvtStop) break;

        if(flags & WorkerEvtRxDone) {
            size_t len = furi_stream_buffer_receive(logger->rx_stream, rx_buf, RX_BUF_SIZE, 0);
            if(len > 0 && logger->file) {
                storage_file_write(logger->file, rx_buf, len);
                // Optional: flush every N bytes or seconds
            }
        }
    }

    return 0;
}

int32_t gpio_logger_app(void* p) {
    UNUSED(p);
	
	main_thread_id = furi_thread_get_id(furi_thread_get_current());

    // Allocate logger
    UartLogger logger;
    logger.rx_stream = furi_stream_buffer_alloc(RX_BUF_SIZE, 1);

    // Open log file
    Storage* storage = furi_record_open("storage");
    logger.file = storage_file_alloc(storage);
    if(!storage_file_open(logger.file, LOG_FILE_PATH, FSAM_WRITE, FSOM_CREATE_ALWAYS)) {
        FURI_LOG_E("UART_LOGGER", "Failed to open %s", LOG_FILE_PATH);
        return 1;
    }

    // Acquire and configure UART
    logger.serial = furi_hal_serial_control_acquire(FuriHalSerialIdUsart);
    furi_hal_serial_init(logger.serial, UART_BAUDRATE);
    furi_hal_serial_async_rx_start(logger.serial, uart_rx_cb, &logger, false);

    // Start RX thread
    logger.rx_thread = furi_thread_alloc();
    furi_thread_set_name(logger.rx_thread, "UartLoggerRx");
    furi_thread_set_stack_size(logger.rx_thread, 1024);
    furi_thread_set_context(logger.rx_thread, &logger);
    furi_thread_set_callback(logger.rx_thread, uart_logger_worker);
    furi_thread_start(logger.rx_thread);

    // Run until user exits app
	ViewPort* view_port = view_port_alloc();
	view_port_draw_callback_set(view_port, draw_callback, NULL);
	view_port_input_callback_set(view_port, input_callback, NULL);


	Gui* gui = furi_record_open("gui");
	gui_add_view_port(gui, view_port, GuiLayerFullscreen);


	// Wait for Back button to be pressed
	furi_thread_flags_wait(APP_EXIT_FLAG, FuriFlagWaitAny, FuriWaitForever);


	gui_remove_view_port(gui, view_port);
	view_port_free(view_port);
	furi_record_close("gui");


		
    // Cleanup
    furi_thread_flags_set(furi_thread_get_id(logger.rx_thread), WorkerEvtStop);
    furi_thread_join(logger.rx_thread);
    furi_thread_free(logger.rx_thread);
    furi_stream_buffer_free(logger.rx_stream);

    furi_hal_serial_async_rx_stop(logger.serial);
    furi_hal_serial_deinit(logger.serial);
    furi_hal_serial_control_release(logger.serial);

    storage_file_close(logger.file);
    storage_file_free(logger.file);
    furi_record_close("storage");
    furi_record_close("dialogs");

    return 0;
}
