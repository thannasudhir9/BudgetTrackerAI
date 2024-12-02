// filename : downloadPDF.js
// Show loading indicator

function downloadPageAsPDF() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-white bg-opacity-75';
    loadingDiv.innerHTML = '<div class="spinner-border text-primary"></div>';
    document.body.appendChild(loadingDiv);

    // Initialize jsPDF
    window.jspdf.jsPDF();

    const element = document.getElementById('dashboard-content');
    const options = {
        scale: 2,
        useCORS: true,
        allowTaint: true,
        scrollY: -window.scrollY,
        windowWidth: element.scrollWidth
    };

    html2canvas(element, options).then(canvas => {
        try {
            const { jsPDF } = window.jspdf;
            const pdf = new jsPDF('p', 'mm', 'a4');
            
            // Calculate dimensions
            const imgWidth = 210; // A4 width in mm
            const pageHeight = 295; // A4 height in mm
            const imgHeight = (canvas.height * imgWidth) / canvas.width;
            
            // Add image to PDF
            const imgData = canvas.toDataURL('image/png');
            pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
            
            // Add more pages if content is longer than one page
            let heightLeft = imgHeight;
            let position = -pageHeight;
            
            while (heightLeft >= pageHeight) {
                pdf.addPage();
                pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
                heightLeft -= pageHeight;
                position -= pageHeight;
            }
            
            // Generate filename with date
            const today = new Date();
            const dateStr = today.getFullYear() +
                          String(today.getMonth() + 1).padStart(2, '0') +
                          String(today.getDate()).padStart(2, '0');
            
            // Save PDF
            pdf.save(`BudgetReport_${dateStr}.pdf`);
        } catch (error) {
            console.error('Error generating PDF:', error);
            alert('Failed to generate PDF. Please try again.');
        } finally {
            document.body.removeChild(loadingDiv);
        }
    }).catch(error => {
        console.error('Error capturing page content:', error);
        document.body.removeChild(loadingDiv);
        alert('Failed to capture page content. Please try again.');
    });
}