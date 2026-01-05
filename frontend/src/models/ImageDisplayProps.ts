export interface ImageDisplayProps {
    imagePath?: string;
    description?: string;
    isOpen: boolean;
    onClose: () => void; // Callback function to close the modal
}